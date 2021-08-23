## aws batch & ECR, ECS

### 1. 원하는 실행 docker image 를 ECR 에 push
```
filename = push_docker.py
```
#### Usage
```bash
python push_docker.py --repo [YOUR ECR REPO NAME] --docker [Docker image name:Tag] --path [Dockerfile folder path]

```

### 2. batch 관련 초기화 세팅 with ECR repo
```
filename = initiate.py
```
#### Usage
```bash
python initiate.py --secGroup [YOUR Security Group Name] --computeName [YOUR batch compute environment name] --jobQueue [YOUR jobQueue Name] --jobDefinitionName [YOUR jobDefinition Name] --dockerName [YOUR ECR docker image name (docker:tag)]

```

### 3. testing
```
filename = test.py
```
- submit batch with boto3
#### Usage
```bash
python test.py --jobQueue [YOUR jobQueue Name] --jobDefinitionName [YOUR jobDefinition Name] --jobName [YOUR job name (default : test)] --vcpu [INT default : 1] --memory [INT default : 2000 (MB)]
```

### .env

ACCESS_KEY=[YOUR KEY]
SECRET_KEY=[YOUR KEY]
REGION=ap-[YOUR REGION]

USER_ID=[YOUR USER ID]