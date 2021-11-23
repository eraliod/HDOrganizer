#!python

# this script is used to upload video files to S3
import os
import boto3
import json

from botocore.exceptions import ClientError

# profile_name = os.environ('profile_name')

profile_name = 'hdo-dev'

def hdo_import_file(file_name, file_path, bucket):

    # boto3.setup_default_session(profile_name='hdo-dev')
    boto3.setup_default_session(profile_name=profile_name)

    #Setting up the S3 bucket for upload
    s3 = boto3.resource('s3')

    #set the S3 filename with prefix
    s3_file_path = 'import/'+file_name

    #Setting up the client to check file exists
    try:
        s3.Object(bucket, s3_file_path).load()
        print(f'{file_name} already exists')
    except ClientError:
        s3.Bucket(bucket).upload_file(file_path, s3_file_path)
        print(f'{file_name} uploaded successfully')

    return


for file in os.listdir('project/temp/hd_videos/'):
    file_path = f'project/temp/hd_videos/{file}'
    bucket = 'hdorganizer'

    hdo_import_file(file, file_path, bucket)