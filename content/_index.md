---
title: "AI Application Security"
linkTitle: "AI Application Security"
weight: 1
# archetype: "home"
description: "Workshops"
---


# Deploy the app

This will create aws account, ec2 instance, etc

## Access the instance


```bash
bash
```
### Clone the repo

```bash
cd ~
git clone https://github.com/FortinetCloudCSE/AIAppSecurity-lab.git
``` 

```
cd AIAppSecurity-lab/app/
sudo bash run_docker.sh
```

```
IP=$(curl -s ipinfo.io/ip)
echo "Browse to http://$IP:8080"
```



### Tour the app

### Deploy the docker container

```
cd AIAppSecurity-lab/app/
sudo bash run_docker.sh
```

```
echo "
export OPENAI_API_KEY=
export OPENAI_MODEL=gpt-4.1-mini
export AWS_DEFAULT_REGION=us-east-2
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_SESSION_TOKEN=
export S3_BUCKET_NAME=
" > ~/AIAppSecurity-lab/app/.env

```
IP=$(curl -s ipinfo.io/ip)
echo "Browse to http://$IP:8080"
```

### Test the app

## Exploit the application



## ministep 2