#!/usr/bin/env python

import json
import uuid
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    '''
    HDOrganizer-Convert function pushes any video files saved in the 
    HDOrganizer-import S3 bucket to the AWS Elemental MediaConvert service

    '''
    # setup

    # -- environment variables
    region = os.environ['AWS_DEFAULT_REGION']
    destination_bucket = os.environ['destination_bucket']
    role = os.environ['role']
    application = os.environ['application']

    # -- job variables
    uid = str(uuid.uuid4())
    logger.info(uid)
    original_input_key = event['Records'][0]['s3']['object']['key']  # AWS S3 Event known issue replaces characters in names
    logger.info(original_input_key)
    input_key = original_input_key.replace('+',' ')  # S3 event replacing spaces with + 
    logger.info(input_key)
    input_bucket = event['Records'][0]['s3']['bucket']['name']
    logger.info(input_bucket)
    input = 's3://'+input_bucket+'/'+input_key
    logger.info(input)
    destination = destination_bucket+input_key
    logger.info(destination)

    # create job parameters

    # -- Tags
    tags = {}
    tags['tags'] = 'hdorganizer'

    # -- UserMetaData
    metadata = {}
    metadata['uid'] = uid
    metadata['application'] = application
    metadata['input'] = input
    logger.info(json.dumps(metadata))

    # -- Settings
    # -- -- Load base settings from job.json file
    with open("job.json", "r") as jsonfile:
        settings = json.load(jsonfile)
    # -- -- Update the input and output values in the job.json definition
    settings['Inputs'][0]['FileInput'] = input
    settings['OutputGroups'][0]['OutputGroupSettings']['FileGroupSettings']['Destination'] = destination
    logger.info(json.dumps(settings)) 

    # find MediaConvert API URL
    mediaconvert_client = boto3.client('mediaconvert', region_name=region)
    endpoints = mediaconvert_client.describe_endpoints()

    # create an AWS client session
    client = boto3.client('mediaconvert', region_name=region, endpoint_url=endpoints['Endpoints'][0]['Url']) #might need to add parameter: verify=False
    
    # send Create Job command to Mediaconvert
    job = client.create_job(Role=role, UserMetadata=metadata, Settings=settings, Tags=tags)

    return {
        'statusCode': 200,
        'headers': {'Content-Type':'application/json'},
        'body': json.dumps(job, indent=4, sort_keys=True, default=str)    
    }
