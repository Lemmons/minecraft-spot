#!/usr/bin/env python3

import json
import logging
import os
import os.path
import sys
import tarfile
import tempfile
import time

import arrow
import boto3
import docker
import requests

logging.basicConfig(stream=sys.stdout,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG if os.environ.get('DEBUG') == "TRUE" else logging.INFO,
)
LOGGER = logging.getLogger('check_termination.py')

MINECRAFT_DATA = '/data'
S3_BUCKET = os.environ.get('S3_BUCKET')
LIFECYCLE_HOOK_NAME = os.environ.get('LIFECYCLE_HOOK_NAME')

def get_boto_client(service):
    if not get_boto_client._clients.get(service):
        get_boto_client._clients[service] = boto3.client(service)
    return get_boto_client._clients[service]
get_boto_client._clients = {}

def get_docker_client():
    if not get_docker_client._client:
        get_docker_client._client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    return get_docker_client._client
get_docker_client._client = None

def get_minecraft():
    if not get_minecraft._container:
        get_minecraft._container = get_docker_client().containers.get('minecraft')
    return get_minecraft._container
get_minecraft._container = None

#TODO: Might want to break backup stuff into it's own file/service
def light_backup(force_backup=False):
    if force_backup:
        LOGGER.info('backing-up minecraft')
        minecraft = get_minecraft()
        if minecraft.status != "exited": #TODO: also ensure minecraft is running (healthy?)
            minecraft.exec_run('rcon-cli ftb backup start') #TODO: check output and wait for backup to finish? Or poll backup index file

    LOGGER.info('saving minecraft backup to s3')
    backups_path = os.path.join(MINECRAFT_DATA, 'backups')
    backups_index = os.path.join(backups_path, 'backups.json')

    backups = {backup['time']: backup for backup in json.load(backups_index) if backup['success']==True}
    latest_backup = backups[max(backups.keys())]
    save_to_s3(os.path.join(backups_path, latest_backup['file']), 'backups/light.zip')

    get_last_light_backup_time._time = time.time()

    #TODO: maybe also gzip and upload the rest of the folder (exclusing backups and saves)

def get_last_light_backup_time():
    if not get_last_light_backup_time.time:
        client = get_boto_client('s3')
        response = client.head_object(filename, S3_BUCKET, 'backups/light.zip')
        get_last_light_backup_time.time = response['LastModified'].timestamp()
    LOGGER.info('Last backup was {} seconds ago'.format(time.time() - get_last_light_backup_time.time))
    return get_last_light_backup_time._time
get_last_light_backup_time._time = None

def save_to_s3(filename, key):
    LOGGER.info('Uploading {} to s3 at {}'.format(filename, key))
    client = get_boto_client('s3')
    client.upload_file(filename, S3_BUCKET, key)

def stop_and_backup_minecraft():
    LOGGER.info('stopping minecraft')
    minecraft = get_minecraft()
    if minecraft.status != "exited":
        minecraft.exec_run('rcon-cli stop') #TODO: check output and make sure it was successful

    while minecraft.status != "exited":
        minecraft.reload()
        LOGGER.info('waiting for minecraft to close')
        time.sleep(1)

    LOGGER.info('backing up minecraft')
    key = "backups/latest.tgz"
    with tempfile.NamedTemporaryFile() as file:
        with tarfile.open(fileobj=file, mode='w:gz') as tar:
            tar.add(MINECRAFT_DATA)
            save_to_s3(file.name, key)


def get_instance_details():
    client = get_boto_client('autoscaling')
    instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text
    return client.describe_auto_scaling_instances(InstanceIds=[instance_id])['AutoScalingInstances'][0]

def get_automatic_termination_time():
    response = requests.get('http://169.254.169.254/latest/meta-data/spot/termination-time')
    if not response.ok:
        return
    return response.text

#TODO: Add periodic backups of world apart from shutdown backup of server
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
        client = get_boto_client('autoscaling')
        client.complete_lifecycle_action(
            LifecycleHookName=LIFECYCLE_HOOK_NAME,
            AutoScalingGroupName=instance_details['AutoScalingGroupName'],
            LifecycleActionResult='CONTINUE',
            InstanceId=instance_details['InstanceId'],
        )

    return terminate

def main():
    terminate = False
    while not terminate:
        terminate = run()
        LOGGER.debug('Waiting for termination')
        time.sleep(1)

if __name__ == "__main__":
    main()
