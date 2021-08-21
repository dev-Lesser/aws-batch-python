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
    parser.add_argument('--jobQueue', required=True, help="jobQueue name")
    parser.add_argument('--jobDefinitionName', required=True, help="jobDefinitionName name")
    parser.add_argument('--jobName', default='test',help="Job name")
    parser.add_argument('--vcpu', default=1, help="number VCPU")
    parser.add_argument('--memory', default=1000, help="memory")

    args = parser.parse_args()
    

    jobQueueName = args.jobQueue
    jobDefinitionName = args.jobDefinitionName
    jobName = args.jobName
    vcpu = args.vcpu
    memory = args.memory

    batch = boto3.client(
        'batch',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION,
    )

    batch.submit_job(
        jobName=jobName,
        jobQueue = jobQueueName,
        jobDefinition=jobDefinitionName,
        containerOverrides={
            'vcpus': vcpu,
            'memory': memory,
            'command': [],

        }
    )