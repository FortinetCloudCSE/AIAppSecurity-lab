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

Use AWS Systems Manager Session Manager to open a shell on the lab instance.

1. In the lab portal, click Start Lab if the environment is not already running.

	![Step 1: Start the lab](/img/1.png)

2. When the lab is ready, click Open Console. Copy the username, password, and AWS account ID shown on the page because you will need them for sign-in.

	![Step 2: Open the AWS console and review the lab credentials](/img/2.png)

3. Sign in as an IAM user with the provided AWS account ID, IAM username, and password, then click Sign in.

	![Step 3: Sign in to the AWS console as the lab IAM user](/img/3.png)

4. In the AWS console search bar, enter EC2 and select the EC2 service.

	![Step 4: Search for the EC2 service](/img/4.png)

5. From the EC2 dashboard, click Instances running or select Instances from the left navigation.

	![Step 5: Open the EC2 instances page](/img/5.png)

6. Select the running lab instance, open the Connect actions menu, and choose Connect.

	![Step 6: Open the connect dialog for the instance](/img/6.png)

7. In the Connect to instance page, open the SSM Session Manager tab and click Connect.

	![Step 7: Connect with SSM Session Manager](/img/7.png)

8. When the session opens, start a shell by running the command below.

	![Step 8: Session Manager terminal connected to the instance](/img/8.png)

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