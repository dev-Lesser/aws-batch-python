import boto3
from dotenv import load_dotenv
import os
import base64
import docker
import argparse

if __name__ == '__main__':
    load_dotenv(verbose=True)
    ACCESS_KEY = os.getenv('ACCESS_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY')
    REGION = os.getenv('REGION')
    USER_ID = os.getenv('USER_ID')

    parser = argparse.ArgumentParser(description='Process Create ECR repo & push docker image')
    parser.add_argument('--secGroup', required=True, help="security group name")
    parser.add_argument('--computeName', required=True, help="Computing name for aws Batch")
    parser.add_argument('--jobQueue', required=True, help="jobQueue name")
    parser.add_argument('--jobDefinitionName', required=True, help="jobDefinitionName name")
    parser.add_argument('--dockerName', required=True, help="ECR repo dockerName")

    args = parser.parse_args()
    

    SECURITY_GROUP_NAME = args.secGroup
    computeEnvironmentName = args.computeName
    jobQueueName = args.jobQueue
    jobDefinitionName = args.jobDefinitionName
    dockerName = args.dockerName

    batch = boto3.client(
        'batch',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION,
    )

    ec2 = boto3.client(
        service_name='ec2',
        region_name='ap-northeast-2',
        endpoint_url='https://ec2.{region}.amazonaws.com'.format(region=REGION),
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )
    # VPC setting
    vpcs = ec2.describe_vpcs(
        DryRun=False,
    )
    vpc_default = [i['VpcId'] for i in vpcs['Vpcs'] if i['CidrBlock']=='172.31.0.0/16'][0] # default value
    print( 'VPC default ID : [{}]'.format(vpc_default))

    # GET subnet
    subnets = ec2.describe_subnets(
        Filters=[
            {
                'Name': 'vpc-id',
                'Values': [
                    vpc_default,
                ],
            },
        ],
        DryRun=False,
    )
    subnet_ids = [i['SubnetId']for i in subnets['Subnets']]
    print('Subnet ids {}'.format(subnet_ids))

    # create security group
    sec_group = ec2.create_security_group(
        Description= SECURITY_GROUP_NAME + "of VPC {}".format(vpc_default), # require
        GroupName=SECURITY_GROUP_NAME, # require
        VpcId=vpc_default,
        DryRun=False
    )

    # create compute environment
    response = batch.create_compute_environment(
        computeEnvironmentName=computeEnvironmentName,
        type='MANAGED',
        computeResources={
            'type': 'EC2',
            'allocationStrategy': 'BEST_FIT',
            'minvCpus': 0,
            'maxvCpus': 256,
            'desiredvCpus': 0,
            'bidPercentage': 100,
            'securityGroupIds': [
                sec_group['GroupId'], 
            ],
            'instanceTypes': ['m4.large'],
            'instanceRole':'arn:aws:iam::{user_id}:instance-profile/ecsInstanceRole'.format(user_id=USER_ID), # 8 digits
            'subnets': subnet_ids
        }
    )
    r = batch.describe_compute_environments(computeEnvironments=[computeEnvironmentName])
    assert len(r['computeEnvironments']) != 0, "there is no compute environment name : {}".format(computeEnvironments)

    # create job queue
    batch.create_job_queue(
        jobQueueName= jobQueueName,
        state='ENABLED',
        priority=0,
        computeEnvironmentOrder=[
            {
                'order': 0,
                'computeEnvironment': computeEnvironmentName # 만든 컴퓨팅 환경 이름을 넣어줌
            },
        ],
    
    )
    # create job definition with ecr repo
    imageName = '{user_id}.dkr.ecr.{region}.amazonaws.com/{dockerName}'.format(user_id=USER_ID, region=REGION, dockerName=dockerName)
    batch.register_job_definition(
        jobDefinitionName=jobDefinitionName,
        type='container',
        containerProperties={
            'image': imageName,
            'resourceRequirements': [{'type': "VCPU", 'value': "1"}, {'type': "MEMORY", 'value': "2000"}] # cpu1 memory 2000MB

        },
        retryStrategy= {'attempts': 1}, # retry
        timeout={
            'attemptDurationSeconds': 3600
        },
        platformCapabilities=[
            'EC2'
        ]
    )

    print("""
    Finished initiate
    [Compute Environment] \t : %s
    [jobQueueName] \t : %s
    [jobDefinitionName] \t : %s
    [ECR repo] \t : %s
    """ % (computeEnvironmentName, jobQueueName, jobDefinitionName, imageName))