#aws - python CLI tool 

The AWS CLI Manager Tool is a command-line tool designed for managing AWS services easily. The tool supports managing Route53, S3, and EC2 services, allowing you to create, edit, and delete objects.

Requirements:
 Before using the tool, ensure the following requirements are met:
- AWS Account – A valid AWS account is required.
- Python – You need to have Python 3.6 to 3.10 installed. If you're using a version older than Python 3.6  or newer version than Python 3.10, you will need to upgrade/downgrade your version of Python 
  in order to use Boto3 and AWS CLI properly. You can download Python from [Python.org.](https://www.python.org/downloads/)
- Boto3 – A Python library for interacting with AWS services. To install:
  run the command "pip install boto3"
- AWS CLI – AWS Command Line Interface is required. To install it:
  run the command "pip install awscli"
- Configure AWS CLI – Run the following command to configure your AWS CLI by entering your AWS access key and secret key:
  run the command "aws configure"
  
  
How to Clone the Project and Run the Tool:
- Clone the GitHub Repository
  To get the tool, you need to clone the repository to your local machine. Open your terminal and run the following command:
  git clone **https://github.com/shirlevi12/python-exe.git**
  This will clone the project into a folder named python-exe
- Navigate to the Project Folder
- Run the Tool
  The main script to run the tool is main.py. You can execute the script with Python:
  python main.py


Available Services and Features:
-  Route 53
     Create Hosted Zone – Create a new hosted zone in Route 53.
     Create DNS Records – Create DNS records within your hosted zone.
     Edit DNS Records – Modify existing DNS records created via the cli.
     Delete DNS Records – Delete DNS records from your hosted zone created via the cli.
- S3
     Create Public/Private Bucket – Specify whether to create a public or private bucket.
     Upload File to Bucket – Upload a file to a bucket you created via the cli.
     List Buckets – Display a list of all S3 buckets created via the CLI.
- EC2
     Create EC2 Instance – Create an EC2 instance with either Ubuntu or Amazon Linux OS using the t3.nano or t4g.nano instance type.
     Start and Stop EC2 Instances – Start or stop EC2 instances created via the CLI.
     List EC2 Instances – Display a list of all EC2 instances created via the CLI.
     
Credits
The tool was developed by Shir Levian.

 DocumentationLinks:
 
- [Route 53 - Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html)
- [S3 - Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
- [EC2 - Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html)
- [IAM - Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html)


