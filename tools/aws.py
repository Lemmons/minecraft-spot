import logging

import boto3

import spot_tools.logger

spot_tools.logger.setup_logging()
LOGGER = logging.getLogger(__name__)

def get_boto_client(service):
    if not get_boto_client._clients.get(service):
        get_boto_client._clients[service] = boto3.client(service)
    return get_boto_client._clients[service]
get_boto_client._clients = {}

def save_to_s3(filename, bucket, key):
    LOGGER.info('Uploading {} to s3 at {}'.format(filename, key))
    client = get_boto_client('s3')
    client.upload_file(filename, bucket, key)

def download_from_s3(filename, bucket, key):
    client = get_boto_client('s3')
    client.download_file(bucket, key, filename)
