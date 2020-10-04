import os
import logging

import boto3
import requests

import spot_tools.backup
import spot_tools.logger

spot_tools.logger.setup_logging()
LOGGER = logging.getLogger(__name__)

LIFECYCLE_HOOK_NAME = os.environ.get('LIFECYCLE_HOOK_NAME')


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
    LOGGER.info('Downloading {} from s3 to {}'.format(key, filename))
    client = get_boto_client('s3')
    client.download_file(bucket, key, filename)


def get_instance_details():
    client = get_boto_client('autoscaling')
    instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text
    return client.describe_auto_scaling_instances(InstanceIds=[instance_id])['AutoScalingInstances'][0]


def get_automatic_termination_time():
    response = requests.get('http://169.254.169.254/latest/meta-data/spot/termination-time')
    if not response.ok:
        return
    return response.text

def check_termination(backup_function):
    terminate = False
    instance_details = get_instance_details()
    automatic_termination_time = get_automatic_termination_time()
    manual_termination = 'Terminating' in instance_details['LifecycleState']

    if automatic_termination_time or manual_termination:
        backup_function()
        terminate = True

    if manual_termination:
        LOGGER.info('Terminating self due manual stop')
        client = get_boto_client('autoscaling')
        client.complete_lifecycle_action(
            LifecycleHookName=LIFECYCLE_HOOK_NAME,
            AutoScalingGroupName=instance_details['AutoScalingGroupName'],
            LifecycleActionResult='CONTINUE',
            InstanceId=instance_details['InstanceId'],
        )

    if not automatic_termination_time and not manual_termination:
        spot_tools.backup.backup_if_needed()

    return terminate


def mark_instance_for_removal():
    LOGGER.info('Marking intance for removal')

    client = get_boto_client('autoscaling')

    instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text
    instance_details = client.describe_auto_scaling_instances(InstanceIds=[instance_id])['AutoScalingInstances'][0]

    client.set_desired_capacity(
        AutoScalingGroupName=instance_details['AutoScalingGroupName'],
        DesiredCapacity=0,
        HonorCooldown=False,
    )
