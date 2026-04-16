---
title: "AI Application Security"
linkTitle: "AI Application Security"
weight: 1
# archetype: "home"
description: "Workshops"
---


## Start The Lab

1. In the lab portal, click Start Lab if the environment is not already running.
   
    [![](https://github.com/FortinetCloudCSE/AIAppSecurity-lab/blob/main/content/1.png?raw=true)](https://github.com/FortinetCloudCSE/AIAppSecurity-lab/blob/main/content/1.png?raw=true)

## Access the instance


2. When the lab is ready, click Open Console. Copy the username, password, and AWS account ID shown on the page because you will need them for sign-in.

[![](https://github.com/FortinetCloudCSE/AIAppSecurity-lab/blob/main/content/2.png?raw=true)](https://github.com/FortinetCloudCSE/AIAppSecurity-lab/blob/main/content/2.png?raw=true)

3. Sign in as an IAM user with the provided AWS account ID, IAM username, and password, then click Sign in.

	[![](https://github.com/FortinetCloudCSE/AIAppSecurity-lab/blob/main/content/3.png?raw=true)](https://github.com/FortinetCloudCSE/AIAppSecurity-lab/blob/main/content/3.png?raw=true)

1. In the AWS console search bar, enter EC2 and select the EC2 service.

[![](https://github.com/FortinetCloudCSE/AIAppSecurity-lab/blob/main/content/4.png?raw=true)](https://github.com/FortinetCloudCSE/AIAppSecurity-lab/blob/main/content/4.png?raw=true)

5. From the EC2 dashboard, click Instances running or select Instances from the left navigation.

[![](https://github.com/FortinetCloudCSE/AIAppSecurity-lab/blob/main/content/5.png?raw=true)](https://github.com/FortinetCloudCSE/AIAppSecurity-lab/blob/main/content/5.png?raw=true)

6. Select the running lab instance, open the Connect actions menu, and choose Connect.

[![](https://github.com/FortinetCloudCSE/AIAppSecurity-lab/blob/main/content/6.png?raw=true)](https://github.com/FortinetCloudCSE/AIAppSecurity-lab/blob/main/content/6.png?raw=true)

7. In the Connect to instance page, open the SSM Session Manager tab and click Connect.

[![](https://github.com/FortinetCloudCSE/AIAppSecurity-lab/blob/main/content/7.png?raw=true)](https://github.com/FortinetCloudCSE/AIAppSecurity-lab/blob/main/content/7.png?raw=true)

8. When the session opens, start a shell by running the command below.

[![](https://github.com/FortinetCloudCSE/AIAppSecurity-lab/blob/main/content/8.png?raw=true)](https://github.com/FortinetCloudCSE/AIAppSecurity-lab/blob/main/content/8.png?raw=true)

	```bash
	bash
	```

You are now connected to the instance through SSM and can continue with the lab.

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
export S3_BUCKET_NAME=
" > ~/AIAppSecurity-lab/app/.env
```
```
IP=$(curl -s ipinfo.io/ip)
echo "Browse to http://$IP:8080"
```

### Test the app

## Exploit the application



## ministep 2