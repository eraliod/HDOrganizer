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
    '''
    HDOrganizer-CleanUp function deletes source video files once the
    smaller transcoded copy appears in the s3 export folder

    '''
    # setup

    # -- environment variables
    region = os.environ['AWS_DEFAULT_REGION']
    source_bucket = os.environ['source_bucket']
    application = os.environ['application']
    
    # -- grab input from s3 event and convert it as needed
    notification = event['Records'][0]['Sns']
    original_input_key = json.loads(notification['Message'])['Records'][0]['s3']['object']['key']  # AWS S3 Event known issue replaces characters in names
    logger.info(original_input_key)
    input_key = original_input_key.replace('+',' ')  # S3 event replacing spaces with + 
    logger.info(input_key)
    file_name = input_key.removeprefix('export/')
    logger.info(file_name)
    s3_file_path = 'import/' + file_name
    logger.info(s3_file_path)
    
    # -- delete the original file after name conversion
    s3 = boto3.resource('s3')
    try:
        file_exists = s3.Object(source_bucket,s3_file_path).load()
        try:
            delete_job = s3.Object(source_bucket,s3_file_path).delete()
            logger.info(f'deleted {s3_file_path}')
            return {
                'statusCode': 200,
                'headers': {'Content-Type':'application/json'},
                'body': f'deleted {s3_file_path} from source s3 \n ' + json.dumps(delete_job, indent=4, sort_keys=True, default=str)
            }
        except Exception as ex:
            logger.error(ex)
    except Exception as ex:
        logger.error(f'{s3_file_path} not available in s3, nothing to delete')
        logger.error(ex)

    return {
        'statusCode': 400,
        'headers': {'Content-Type':'application/json'},
        'body': f"There was a problem deleting {s3_file_path}. See logs"
    }
