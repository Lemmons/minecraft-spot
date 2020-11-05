#!/usr/bin/env python3

import logging
import os

import requests

import spot_tools.aws
import spot_tools.logger

spot_tools.logger.setup_logging()
LOGGER = logging.getLogger(__name__)

ZONE_ID = os.environ.get('ZONE_ID')
FQDN = os.environ.get('FQDN')

def main():
    ip_address = spot_tools.aws.get_ip_address()

    client = spot_tools.aws.get_boto_client('route53')
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
