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

    
    parser = argparse.ArgumentParser(description='Process Create ECR repo & push docker image')
    parser.add_argument('--repo', required=True, help="ECR repo name")
    parser.add_argument('--docker', required=True, help='docker image name:tag')
    parser.add_argument('--path', required=True, help='Want to build docker image folder')
    args = parser.parse_args()
    

    repositoryName = args.repo
    LOCAL_REPOSITORY = args.docker # local docker image name:tag
    DOCKER_FILE_PATH = args.path

    print(repositoryName, LOCAL_REPOSITORY, DOCKER_FILE_PATH)
    ecr = boto3.client(
        service_name='ecr',
        region_name=REGION,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )


    # create ECR repository
    try:
        ecr.create_repository(
            repositoryName=repositoryName,
        )
    except Exception:
        raise Exception("Already exists name : {} repo".format(repositoryName))

    # for docker login
    ecr_credentials = ( ecr.get_authorization_token()['authorizationData'][0])
    ecr_username = 'AWS'


    ecr_password = (
        base64.b64decode(ecr_credentials['authorizationToken'])
        .replace(b'AWS:', b'')
        .decode('utf-8'))
    
    ecr_url = ecr_credentials['proxyEndpoint']
    # https://{userID}.dkr.ecr.{REGION}.amazonaws.com

    docker_client = docker.from_env()
    docker_client.login(
        username=ecr_username, 
        password=ecr_password, 
        registry=ecr_url
    )

    ecr_repo_name = '{}/{}'.format(
        ecr_url.replace('https://', ''), LOCAL_REPOSITORY) # {userID}.dkr.ecr.{REGION}.amazonaws.com/{docker name}:{tag}
    
    repos = ecr.describe_repositories()['repositories'] # exist repo list
    isExist = False
    for repo in repos:
        if repo['repositoryName'] == repositoryName:
            isExist = True


    assert isExist, "No repository : {}".format(repositoryName)

    print("[PROCESS] \t BUILDING DOCKER IMAGE")
    image, build_log = docker_client.images.build(
        path=DOCKER_FILE_PATH, 
        tag=LOCAL_REPOSITORY, 
        rm=True
    )
    print(list(build_log))

    image.tag(ecr_repo_name, tag='latest')
    print("[PROCESS] \t PUSH DOCKER IMAGE to ECR")
    push_log = docker_client.images.push(ecr_repo_name, tag='latest')
    print(push_log)

    print("[PROCESS] \t DONE \n ECR repo : {}".format(ecr_repo_name))