#!python

# this script is used to upload video files to S3
import os
import boto3
import logging
from botocore.exceptions import ClientError
from dotenv import load_dotenv


def hdo_import_file(file_name, file_path, bucket):

    # Establish session using environment variables from config/env
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

    session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    #Setting up the S3 bucket for upload
    s3 = session.client('s3')

    #set the S3 filename with prefix
    s3_file_path = 'import/'+file_name

    #set the local complete file path
    local_file_path = file_path + os.sep + file_name
    
    #Setting up the client to check file exists
    try:
        s3.head_object(Bucket=bucket, Key=s3_file_path)
        logging.warning(f'{file_name} already exists')
# TODO - Better Error handling - https://stackoverflow.com/questions/33842944/check-if-a-key-exists-in-a-bucket-in-s3-using-boto3
    except ClientError:
        # s3.put_object(Body=b'local_file_path', Bucket=bucket, Key=s3_file_path)
        s3.upload_file(local_file_path, bucket, s3_file_path)
        logging.info(f'{file_name} uploaded successfully')

    return

if __name__ == '__main__':
    load_dotenv()
    # logging.basicConfig(
    #     # filename='hdo_upload.log',
    #     encoding='utf-8',
    #     format='%(asctime)s %(levelname)-8s %(message)s',
    #     level=logging.INFO,
    #     datefmt='%Y-%m-%d %H:%M:%S')

    # for file in os.listdir('project/temp/hd_videos/'):
    #     file_path = 'project/temp/hd_videos'
    #     bucket = 'hdorganizer'
    #     print(file)

        # hdo_import_file(file, file_path, bucket)

    # file_path = 'project/temp/hd_videos'
    # bucket = 'hdorganizer'
    # hdo_import_file('Puppies - 69168.mp4',file_path,bucket)

