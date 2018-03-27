#!/usr/bin/env python3

import logging
import os
import sys
import tarfile
import tempfile

import boto3
import requests

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
LOGGER = logging.getLogger('set_route.py')

MINECRAFT_DATA = '/data'
S3_BUCKET = os.environ.get('S3_BUCKET')
ZONE_ID = os.environ.get('ZONE_ID')
FQDN = os.environ.get('FQDN')

def get_boto_client(service):
    if not get_boto_client._clients.get(service):
        get_boto_client._clients[service] = boto3.client(service)
    return get_boto_client._clients[service]
get_boto_client._clients = {}

def main():
    ip_address = requests.get('http://169.254.169.254/latest/meta-data/public-ipv4').text

    client = get_boto_client('route53')
    change_batch = {'Changes': [
        {
            'Action': 'UPSERT',
            'ResourceRecordSet': {
                'Name': FQDN,
                'Type': 'A',
                'TTL': 60,
                'ResourceRecords': [{'Value': ip_address}],
            }
        }
    ]}
    LOGGER.info('Updating Route53 with change batch: {}'.format(change_batch))
    client.change_resource_record_sets(HostedZoneId=ZONE_ID, ChangeBatch=change_batch)
    LOGGER.info('Route53 Updated')

if __name__ == "__main__":
    main()
