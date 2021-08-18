## aws batch & ECR, ECS

### 1. 원하는 실행 docker image 를 ECR 에 push
```
filename = push_docker.py
```

### 2. batch 관련 초기화 세팅 with ECR repo
```
filename = initiate.py
```
### 3. testing
```
filename = test.py
```
- submit batch with boto3


### .env

ACCESS_KEY=[YOUR KEY]
SECRET_KEY=[YOUR KEY]
REGION=ap-[YOUR REGION]

USER_ID=[YOUR USER ID]