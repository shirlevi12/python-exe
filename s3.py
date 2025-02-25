import json
import boto3
from botocore.exceptions import ClientError
import os
import re

s3 = boto3.client('s3')
iam_client = boto3.client('iam')
user_response = iam_client.get_user()
user_name = user_response['User']['UserName']

CREATE_S3 = "1"
UPLOAD_FILE = "2"
LIST_OF_BUCKETS_CREATED_BY_CLI = "3"
MAX_LETTERS_FOR_AN_OBJECT_NAME = 1024
CONFIRM = "yes"
MIN_LETTERS_FOR_BUCKET_NAME = 3
MAX_LETTERS_FOR_BUCKET_NAME = 63

def is_valid_bucket_name(bucket_name):
    
    if len(bucket_name) < MIN_LETTERS_FOR_BUCKET_NAME or len(bucket_name) > MAX_LETTERS_FOR_BUCKET_NAME:
        return False
    
    if bucket_name[0] in ['-', '_'] or bucket_name[-1] in ['-', '_']:
        return False
    
    if not re.match(r'^[a-z0-9-._]+$', bucket_name):
        return False

    return True

def create_s3_bucket():
    while True:
        bucket_name = input("Enter a name for your bucket: ")
        
        if not is_valid_bucket_name(bucket_name):
            print(f"The name {bucket_name} is invalid. Please use only lowercase letters, numbers.")
            continue
        
        try:
            
            s3.head_bucket(Bucket=bucket_name)
            print(f"The name {bucket_name} already exists.")
            continue
        except ClientError as error:
            if error.response['Error']['Code'] == '404':
                pass
            elif error.response['Error']['Code'] == '403':
                print(f"The name {bucket_name} is not allowed or already exists globally.")
                continue

        public_or_private = input("Choose between 'public' or 'private' access: ").lower()
        if public_or_private == "public":
            validate_answer = input("Are you sure you want public access? yes/no ").lower()
            if validate_answer == CONFIRM:
                public_or_private = "public-read"
            else:
                break
        elif public_or_private != "private" and public_or_private != "public":
            print("You typed something wrong.")
            break
        
        
        s3.create_bucket(
            Bucket=bucket_name,
        )
        print(f"Bucket {bucket_name} created.")
        

        s3.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={
                'TagSet': [
                    {'Key': 'CreatedBy', 'Value': 'cli'},
                    {'Key': 'Owner', 'Value': user_name}
                ]
            }
        )

        if public_or_private == "public-read":
            s3.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': False,
                    'IgnorePublicAcls': False,
                    'BlockPublicPolicy': False,
                    'RestrictPublicBuckets': False
                }
            )

            public_read_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",  
                        "Action": "s3:GetObject",  
                        "Resource": f"arn:aws:s3:::{bucket_name}/*" 
                    }
                ]
            }

            policy_string = json.dumps(public_read_policy)

            try:
                s3.put_bucket_policy(
                    Bucket=bucket_name,
                    Policy=policy_string
                )
                print(f"Public read policy has been applied to the bucket {bucket_name}.")
            except ClientError as e:
                print(f"An error occurred while applying the policy: {e}")

        ask_for_another_bucket = input("Would you like to create another bucket? yes/no ").lower()

        if ask_for_another_bucket != CONFIRM:
            break

def upload_file():
    while True:
        bucket_name = input("enter the bucket name: ")
        if not is_valid_bucket_name(bucket_name):
            return print("Invalid bucket name")
        
        try:
            response = s3.get_bucket_tagging(Bucket=bucket_name)
        except Exception as e:
            print(f"error with retrieving bucket: {e}")
            return
        
        tags = response['TagSet']
        from_cli = False
        for tag in tags:
            if tag['Key'] == 'CreatedBy':
                from_cli = True
        if not from_cli :
            print(f'the bucket {bucket_name} cannot be selected ' )
        else:
            break

    while True:
        file_path = input("enter the file path: ")
        if os.path.exists(file_path):
            break
        else:
            print(f"the path ({file_path}) you entered is incorrect")

    bool_obj_name = input("would you like to add object name? yes/no ")
    if bool_obj_name.lower() == CONFIRM:
        while True:
            object_name = input('enter the object file name: ')
            if ' ' in object_name:
                print('the name you entered is incorrect, the name should be without any spaces')
            elif object_name[-1] == '/' :
                print('the name you entered is incorrect, the last char cant be /')
            elif len(object_name) > MAX_LETTERS_FOR_AN_OBJECT_NAME:
                print('the name you entered is incorrect, the len cant be above 1024')
            else:
                break
        s3.upload_file(file_path, bucket_name, object_name)
        
    else:
        object_name = os.path.basename(file_path)
        s3.upload_file(file_path, bucket_name, object_name)

    print("you have successfully uploaded a file")
    ask_for_another_file = input("Would you like to upload another file? yes/no ").lower()
    if ask_for_another_file == CONFIRM:
        upload_file()

def list_s3_buckets():
    tag_key = 'CreatedBy'
    tag_value = 'cli'
    list_response = s3.list_buckets()
    buckets = list_response['Buckets']
    buckets_with_tag = []

    for bucket in buckets:
        bucket_name = bucket['Name']
        try:
            tags_response = s3.get_bucket_tagging(Bucket=bucket_name)

            for tag in tags_response.get('TagSet', []):
                if tag['Key'] == tag_key and tag['Value'] == tag_value:
                    buckets_with_tag.append(bucket_name)
        except ClientError:
            pass
    
    return buckets_with_tag
    

def main():
    while True:
        ask_for_action = input("enter a number for an action:\n[1]create bucket\n[2]upload file \n[3]list buckets created by the cli\n")
        if ask_for_action == CREATE_S3:
            create_s3_bucket()
        elif ask_for_action == UPLOAD_FILE:
            upload_file()
        elif ask_for_action == LIST_OF_BUCKETS_CREATED_BY_CLI:
            buckets_with_tag = list_s3_buckets()
            print("List of s3 buckets created by the cli :", buckets_with_tag)
        else:
            print("no such option, try again")

        ask_for_another_action = input("Would you like to do another action? yes/no ").lower()
        if ask_for_another_action != CONFIRM:
            break
    
if __name__ == "__main__":
    try:
      main()
    except KeyboardInterrupt:
        exit()
