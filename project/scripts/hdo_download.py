#!python

# This script is used to download completed (converted) video files back to the source machine

import os
import boto3
import json
import logging
from lock import lock_file_exists, make_lock_file, release_lock_file
from botocore.exceptions import ClientError
from dotenv import load_dotenv

def hdo_get_sqs_message(sqs_queue_url,region_name):

    # Establish session using environment variables from config/env
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

    session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY,region_name=region_name)

    #Setting up the S3 bucket for upload
    sqs = session.client('sqs')

    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl = sqs_queue_url,
        AttributeNames = [
            'SentTimestamp'
        ],
        MaxNumberOfMessages = 1,
        MessageAttributeNames = [
            'All'
        ]
        ,VisibilityTimeout = 60 #declaring here will override the "default" (set in the queue)
    )

    if 'Messages' in response:
        receipt_handle = response['Messages'][0]['ReceiptHandle']
        logging.info('--------receipt_handle--------')
        logging.info(receipt_handle)

        body = response['Messages'][0]['Body']
        message = json.loads(body)['Message']
        if 'Records' in json.loads(message):
            original_input_key = json.loads(message)['Records'][0]['s3']['object']['key']
            logging.info(original_input_key)
            input_key = original_input_key.replace('+',' ')  # S3 event replacing spaces with + 
            logging.info('-------input_key---------')
            logging.info(input_key)
        else:
            logging.info('there are no Records in this SQS message. Skip')
            input_key = None

        return receipt_handle, input_key
        
    else:
        raise ValueError('SQS has no messages... Terminating')

def hdo_download_file(key,bucket,transcode_load_folder):

    # Establish session using environment variables from config/env
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

    session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    #Setting up the S3 bucket for upload
    s3 = session.client('s3')

    #set the S3 object and local download destination
    s3_file_path = key
    file_path = transcode_load_folder + os.sep + key[7:]

    #download file
    s3.download_file(bucket, s3_file_path, file_path)
    logging.info(f'{key} downloaded successfully from S3')


def hdo_delete_file(key,bucket):

    # Establish session using environment variables from config/env
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    #Setting up the S3 bucket for upload
    s3 = session.client('s3')

    #set the S3 object and local download destination
    s3_file_path = key
    
    s3.delete_object(Bucket=bucket,Key=s3_file_path)
    logging.info(f'{key} deleted successfully from S3')


def hdo_delete_sqs_message(receipt_handle,sqs_queue_url,region_name):

    # Establish session using environment variables from config/env
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

    session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY,region_name=region_name)

    #Setting up the S3 bucket for upload
    sqs = session.client('sqs', region_name=region_name)
    sqs.delete_message(
        QueueUrl = sqs_queue_url,
        ReceiptHandle = receipt_handle
    )
    logging.info('Received and deleted SQS message')

def main():
    logging.basicConfig(
        # filename='hdo_download.log',
        encoding='utf-8',
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    #Set aws calls back to WARNING to avoid verbose messages
    logging.getLogger('botocore').setLevel(logging.WARNING) 

    #Load environment variables
    load_dotenv()
    region_name = os.getenv('region_name')
    sqs_queue_url = os.getenv('sqs_queue_url')
    bucket = os.getenv('bucket')
    transcode_load_folder = os.getenv('download')

    logging.info('----- BEGIN PROCESS -----')
    if not lock_file_exists('python_running.lock'):
        make_lock_file('python_running.lock','Running HDOrganizer downloads')
        while True:  
            logging.info('Poll Amazon SQS')
            try:
                sqs_message_details = hdo_get_sqs_message(sqs_queue_url,region_name)
            except Exception as ex:
                logging.error(ex)
                break
                # logging.info('----- END PROCESS -----')
                # exit()

            receipt_handle = sqs_message_details[0]
            input_key = sqs_message_details[1]

            if input_key:
                try:
                    hdo_download_file(input_key,bucket,transcode_load_folder)
                    hdo_delete_sqs_message(receipt_handle,sqs_queue_url,region_name)
                    hdo_delete_file(input_key,bucket)
                except Exception as e:
                    logging.warning(f'{input_key} did not download, sqs message retained and will return to the queue after visibility timeout')
                    logging.error(e)
                    continue
            else:
                continue
        
        release_lock_file('python_running.lock')  
        logging.info('----- END PROCESS -----')
    else:
        logging.info('----- END PROCESS -----')              

if __name__ == '__main__':
    main()