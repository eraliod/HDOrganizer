#!python

# This script is used to download completed (converted) video files back to the source machine


# Local docker has to run this via cron only if not already running. One way to do this is to
#   run a bash script via cron that runs the py script only if a lock file is not present.
#   See here: https://serverfault.com/questions/237710/dont-run-cron-job-if-already-running


from logging import error
import os
import boto3
import json

from botocore.exceptions import ClientError

# profile_name = os.environ('profile_name')
# region_name = os.environ('region_name')
# sqs_queue_url = os.environ('sqs_queue_url')

profile_name = 'hdo-dev'
region_name = 'us-east-2'
sqs_queue_url = 'https://sqs.us-east-2.amazonaws.com/361744900418/HDOrganizer-download-queue'

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
    print('this is the response:')
    print(response)
    if 'Messages' in response:
        # print('-------message---------')
        message = response['Messages'][0]
        # # message = response.get("Messages",[])
        # print(message)
        # print('-------receipt handle---------')
        receipt_handle = message['ReceiptHandle']
        # print(receipt_handle)
        # print('-------body---------')
        message_body = json.loads(message['Body'])
        # print(message_body)
        # print('-------oritinal_input_key---------')
        original_input_key = message_body['Records'][0]['s3']['object']['key']
        # print(original_input_key)
        print('-------input_key---------')
        input_key = original_input_key.replace('+',' ')  # S3 event replacing spaces with + 
        print(input_key)
        print('--------receipt_handle--------')
        print(receipt_handle)

        return receipt_handle, input_key
        
    else:
        print('SQS has no messages')
        raise ValueError('SQS has no messages')

    
transcode_load_folder = 'project/temp/downloads/'
bucket = 'hdorganizer'

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
    print(f'{key} downloaded successfully')


def hdo_delete_file(key):

    boto3.setup_default_session(profile_name=profile_name)

    #Setting up the S3 bucket for upload
    s3 = boto3.resource('s3')

    #set the S3 object and local download destination
    s3_file_path = key
    
    s3.Object(bucket,s3_file_path).delete()
    print(f'{key} deleted successfully')


def hdo_delete_sqs_message(receipt_handle):

    boto3.setup_default_session(profile_name=profile_name)

    #Setting up the S3 bucket for upload
    sqs = boto3.client('sqs', region_name=region_name)
    sqs.delete_message(
        QueueUrl = sqs_queue_url,
        ReceiptHandle = receipt_handle
    )
    print('Received and deleted message')


print('----- BEGIN PROCESS -----')

while True:  
    print('----- poll SQS -----')
    try:
        sqs_message_details = hdo_get_sqs_message()
    except:
        exit()

    print('----- returned values -----')
    receipt_handle = sqs_message_details[0]
    print(receipt_handle)
    input_key = sqs_message_details[1]
    print(input_key)

    print('----- attempt download + delete -----')
    try:
        hdo_download_file(input_key)
        print('----- file download complete -----')
        hdo_delete_sqs_message(receipt_handle)
        print('----- SQS message deleted -----')
        hdo_delete_file(input_key)
        print('----- file delete complete -----')
    except Exception as e:
        print(f'{input_key} did not download, sqs message retained and will return to the queue after visibility timeout')
        print(e)
        break
next