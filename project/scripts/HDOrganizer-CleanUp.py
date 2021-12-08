#!/usr/bin/env python

import json
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#Set aws calls back to WARNING to avoid verbose messages
logging.getLogger('botocore').setLevel(logging.CRITICAL) 
    
def lambda_handler(event, context):
    
    # -- environment variables
    region = os.environ['AWS_DEFAULT_REGION']
    destination_bucket = os.environ['destination_bucket']
    application = os.environ['application']
    
    # -- grab input from s3 event and convert it as needed
    notification = event['Records'][0]['Sns']
    original_input_key = json.loads(notification['Message'])['Records'][0]['s3']['object']['key']  # AWS S3 Event known issue replaces characters in names
    logger.debug(original_input_key)
    input_key = original_input_key.replace('+',' ')  # S3 event replacing spaces with + 
    logger.debug(input_key)
    file_name = input_key.lstrip('export/')
    logger.debug(file_name)
    s3_file_path = 'import/' + file_name
    logger.debug(s3_file_path)
    
    # -- delete the original file after name conversion
    s3 = boto3.resource('s3')
    try:
        file_exists = s3.Object(destination_bucket,s3_file_path).load()
        try:
            s3.Object(destination_bucket,s3_file_path).delete()
            logger.info(f'deleted {s3_file_path}')
            return {
                'statusCode': 200,
                'body': json.dumps(f'deleted {s3_file_path}')
            }
        except Exception as ex:
            logger.error(ex)
    except Exception as ex:
        logger.error(f'{s3_file_path} not available in s3, nothing to delete')
        logger.error(ex)

    return {
        'statusCode': 400,
        'body': json.dumps(f'There was a problem deleting {s3_file_path}. See logs')
    }
