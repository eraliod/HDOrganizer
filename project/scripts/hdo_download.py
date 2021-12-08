#!python

# This script is used to download completed (converted) video files back to the source machine


# Local docker has to run this via cron only if not already running. One way to do this is to
#   run a bash script via cron that runs the py script only if a lock file is not present.
#   See here: https://serverfault.com/questions/237710/dont-run-cron-job-if-already-running


# from logging import error
import os
import boto3
import json
import logging

from botocore.exceptions import ClientError

# profile_name = os.environ('profile_name')
# region_name = os.environ('region_name')
# sqs_queue_url = os.environ('sqs_queue_url')

profile_name = 'hdo-dev'
region_name = 'us-east-2'
sqs_queue_url = 'https://sqs.us-east-2.amazonaws.com/361744900418/HDOrganizer-download-queue'

transcode_load_folder = 'project/temp/downloads/'
bucket = 'hdorganizer'

def hdo_get_sqs_message():

    boto3.setup_default_session(profile_name=profile_name)

    #Setting up the S3 bucket for upload
    sqs = boto3.client('sqs', region_name=region_name)

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
        ,VisibilityTimeout = 30 #declaring here will override the "default" (set in the queue)
    )

    if 'Messages' in response:
        body = response['Messages'][0]['Body']
        message = json.loads(body)['Message']
        original_input_key = json.loads(message)['Records'][0]['s3']['object']['key']
        input_key = original_input_key.replace('+',' ')  # S3 event replacing spaces with + 
        logging.info('-------input_key---------')
        logging.info(input_key)
        receipt_handle = response['Messages'][0]['ReceiptHandle']
        logging.info('--------receipt_handle--------')
        logging.info(receipt_handle)

        return receipt_handle, input_key
        
    else:
        logging.warning('SQS has no messages... Terminating')
        raise ValueError('SQS has no messages')

def hdo_download_file(key):

    boto3.setup_default_session(profile_name=profile_name)

    #Setting up the S3 bucket for upload
    s3 = boto3.resource('s3')

    #set the S3 object and local download destination
    s3_file_path = key
    file_path = transcode_load_folder + key[7:]

    # s3.Bucket('hdorganizer').download_file('export/Cat - 66004.mp4','123.mp4')
    #download file
    s3.Bucket(bucket).download_file(s3_file_path, file_path)
    logging.info(f'{key} downloaded successfully from S3')


def hdo_delete_file(key):

    boto3.setup_default_session(profile_name=profile_name)

    #Setting up the S3 bucket for upload
    s3 = boto3.resource('s3')

    #set the S3 object and local download destination
    s3_file_path = key
    
    s3.Object(bucket,s3_file_path).delete()
    logging.info(f'{key} deleted successfully from S3')


def hdo_delete_sqs_message(receipt_handle):

    boto3.setup_default_session(profile_name=profile_name)

    #Setting up the S3 bucket for upload
    sqs = boto3.client('sqs', region_name=region_name)
    sqs.delete_message(
        QueueUrl = sqs_queue_url,
        ReceiptHandle = receipt_handle
    )
    logging.info('Received and deleted SQS message')

def main():
    logging.basicConfig(
        # filename='check_empty.log',
        encoding='utf-8',
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    #Set aws calls back to WARNING to avoid verbose messages
    logging.getLogger('botocore').setLevel(logging.WARNING) 

    logging.info('----- BEGIN PROCESS -----')

    while True:  
        logging.info('Poll Amazon SQS')
        try:
            sqs_message_details = hdo_get_sqs_message()
        except Exception as ex:
            logging.error(ex)
            logging.info('----- END PROCESS -----')
            exit()

        receipt_handle = sqs_message_details[0]
        input_key = sqs_message_details[1]

        try:
            hdo_download_file(input_key)
            hdo_delete_sqs_message(receipt_handle)
            hdo_delete_file(input_key)
        except Exception as e:
            logging.warning(f'{input_key} did not download, sqs message retained and will return to the queue after visibility timeout')
            logging.error(e)
            break
    next

if __name__ == '__main__':
    main()