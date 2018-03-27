#!/usr/bin/env python3

import logging
import os
import sys
import tarfile
import tempfile

import boto3

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
LOGGER = logging.getLogger('restore_backup.py')

MINECRAFT_DATA = '/data'
S3_BUCKET = os.environ.get('S3_BUCKET')

def get_boto_client(service):
    if not get_boto_client._clients.get(service):
        get_boto_client._clients[service] = boto3.client(service)
    return get_boto_client._clients[service]
get_boto_client._clients = {}

def main():
    client = get_boto_client('s3')

    key_latest = "backups/latest.tgz"
    LOGGER.info('Restoring backup from {}'.format(key_latest))
    with tempfile.NamedTemporaryFile() as file:
        LOGGER.info('Downloading {} to {}'.format(key_latest, file.name))
        client.download_fileobj(S3_BUCKET, key_latest, file)
        with tarfile.open(name=file.name, mode='r') as tar:
            LOGGER.info('Un-taring {} to {}'.format(file.name, MINECRAFT_DATA))
            tar.extractall(MINECRAFT_DATA + '/..')

if __name__ == "__main__":
    main()
