#!/usr/bin/env python3

import logging
import os
import time

import requests

import spot_tools.aws
import spot_tools.backup
import spot_tools.logger
import spot_tools.minecraft

spot_tools.logger.setup_logging()
LOGGER = logging.getLogger(__name__)

LIFECYCLE_HOOK_NAME = os.environ.get('LIFECYCLE_HOOK_NAME')

def get_instance_details():
    client = spot_tools.aws.get_boto_client('autoscaling')
    instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text
    return client.describe_auto_scaling_instances(InstanceIds=[instance_id])['AutoScalingInstances'][0]

def get_automatic_termination_time():
    response = requests.get('http://169.254.169.254/latest/meta-data/spot/termination-time')
    if not response.ok:
        return
    return response.text

def stop_and_backup_minecraft():
    spot_tools.backup.local_backup_and_save_to_s3()

    LOGGER.info('stopping minecraft')
    minecraft = spot_tools.minecraft.get_minecraft()

    if minecraft.status != "exited":
        minecraft.exec_run('rcon-cli stop')

    spot_tools.backup.others_backup_if_needed()

def run():
    terminate = False
    instance_details = get_instance_details()
    automatic_termination_time = get_automatic_termination_time()
    manual_termination = 'Terminating' in instance_details['LifecycleState']

    if automatic_termination_time or manual_termination:
        stop_and_backup_minecraft()
        terminate = True

    if manual_termination:
        LOGGER.info('Terminating self due manual stop')
        client = spot_tools.aws.get_boto_client('autoscaling')
        client.complete_lifecycle_action(
            LifecycleHookName=LIFECYCLE_HOOK_NAME,
            AutoScalingGroupName=instance_details['AutoScalingGroupName'],
            LifecycleActionResult='CONTINUE',
            InstanceId=instance_details['InstanceId'],
        )

    if not automatic_termination_time and not manual_termination:
        spot_tools.backup.backup_if_needed()

    return terminate

def main():
    terminate = False
    while not terminate:
        terminate = run()
        LOGGER.debug('Waiting for termination')
        time.sleep(1)

if __name__ == "__main__":
    main()
