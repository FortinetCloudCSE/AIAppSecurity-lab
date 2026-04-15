# CloudFormation stack for the AI Agent host

This stack creates:

- one VPC
- one public subnet
- one internet gateway
- one route table
- one security group
- one public EC2 instance with Docker installed

## Deploy

From a machine with the AWS CLI configured, run:

aws cloudformation create-stack \
  --stack-name ai-agent-stack \
  --template-body file://app/cloudformation/ai-agent-vpc-ec2.yaml \
  --parameters \
    ParameterKey=AvailabilityZone,ParameterValue=us-east-1a \
    ParameterKey=KeyName,ParameterValue=your-keypair-name \
    ParameterKey=MyIpCidr,ParameterValue=YOUR_IP/32

## After the stack is ready

1. SSH to the instance using the output public DNS name
2. Confirm Docker is installed:

   sudo docker --version

3. Copy your app files or pull your image and run it manually
4. Browse to the public instance IP on port 8080
