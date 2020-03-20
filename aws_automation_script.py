#Imports
import boto3
import paramiko
import time

#Can be imported from a config file but hardcoded for simplicity
ACCESS_KEY = 'AKIAT5Y6VW7SMTCTTTM3'
SECRET_KEY = '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'
region = 'us-east-2'

#Initializing boto3 session
session = boto3.Session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

#Multiple ways to pass files to EC2 instance for computation:
#1 - *Place files in an S3 bucket and grab from there (made public for simplicity)
#2 - Use Paramiko's SFTP client to transfer files from local to remote

#Create S3 bucket for data
s3 = session.resource('s3', region_name=region)
location = {'LocationConstraint': region}
s3.create_bucket(Bucket='input-rbi-ml', CreateBucketConfiguration=location)

#Upload local data to S3 input bucket

bucket_name = 'input-rbi-ml'

#Uploading the python file for model
s3.meta.client.upload_file('iris_classifier.py', bucket_name, 'iris_classifier.py',ExtraArgs={'ACL':'public-read'})

#Uploading the iris dataset to the bucket
s3.meta.client.upload_file('IRIS.csv', bucket_name, 'IRIS.csv', ExtraArgs={'ACL':'public-read'})

#Uploading the requirements package list for easy pip install
s3.meta.client.upload_file('requirements.txt', bucket_name, 'requirements.txt', ExtraArgs={'ACL':'public-read'})


#Creating an EC2 Instance
ec2 = session.resource('ec2', region_name=region)
instance = ec2.create_instances(
    ImageId='ami-0e01ce4ee18447327',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro',
    KeyName='rbi_ml')

#Sleep because it takes time for instance to initiate to running state
time.sleep(45)

#Printing what instances are currently running
instances = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'pending']}])

for instance in instances:
    print("Currently created instance:", instance.public_dns_name)

time.sleep(20)

try:
    #Creates an SSH Client instance to connect to EC2 instance
    ssh_client = paramiko.SSHClient()
    host = str(instance.public_dns_name)
    #Passing in the ssh key
    key = paramiko.RSAKey.from_private_key_file('./rbi_ml.pem')
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    #Connect to remote machine
    ssh_client.connect(hostname=host, username='ec2-user', pkey=key)

    time.sleep(15)
except:
    print("Connection error occurred.")

#Create S3 bucket called output-rbi-ml
s3.create_bucket(Bucket='output-rbi-ml', CreateBucketConfiguration=location)

#Copy over files from S3 into EC2 instance using SSH client run command
commands = [
    #Gets files from public bucket
    "wget https://input-rbi-ml.s3.us-east-2.amazonaws.com/IRIS.csv",
    "wget https://input-rbi-ml.s3.us-east-2.amazonaws.com/iris_classifier.py",
    "wget https://input-rbi-ml.s3.us-east-2.amazonaws.com/requirements.txt",
    #Installs python3
    "yes | sudo yum install python3",
    #Gets and installs pip
    "curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py",
    "yes | sudo python get-pip.py",
    #Installs all necessary packages
    "python3 -m pip install --user -r requirements.txt",
    #Runs the model
    "python3 iris_classifier.py",
    #Sends code output to output file
    "python3 iris_classifier.py >> output.txt"
    ]

for command in commands:
    stdin , stdout, stderr = ssh_client.exec_command(command)
    print(command)
    time.sleep(22)



#Create SFTP with Paramiko to download output file from EC2 Instance
#(**Reason that AWS CLI was not used was to fully automate this process via script and could 
#not configure credentials)

sftp_client = ssh_client.open_sftp()
try:
    sftp_client.get('output.txt', 'output.txt')
except:
    print('File not found.')
sftp_client.close()

#Upload the code output to output s3 bucket
s3.meta.client.upload_file('output.txt', 'output-rbi-ml', 'output.txt', ExtraArgs={'ACL':'public-read'})

#Close the SSH connection and terminate the instance
inst_id = instance.instance_id

#Closes the SSH connection
ssh_client.close()

#Terminates the created EC2 instance
ec2.instances.terminate(inst_id)


