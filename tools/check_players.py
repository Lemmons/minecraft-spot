#!/usr/bin/env python3

import logging
import os
import time
import re

import boto3
import docker
import requests

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
LOGGER = logging.getLogger('check_players.py')

GRACE_PERIOD = int(os.environ['GRACE_PERIOD'])

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

def mark_instance_for_removal():
    client = boto3.client('autoscaling')

    instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text
    instance_details = client.describe_auto_scaling_instances(InstanceIds=[instance_id])['AutoScalingInstances'][0]

    client.set_desired_capacity(
        AutoScalingGroupName=instance_details['AutoScalingGroupName'],
        DesiredCapacity=0,
        HonorCooldown=False,
    )

PLAYERS_RE = re.compile(r'There are (?P<players>\d*)/\d* players online:')
def get_players():
    minecraft = get_minecraft()
    if minecraft.status == "exited":
        return

    result = minecraft.exec_run('rcon-cli list')
    if result[0] != 0:
        return
    players_raw = result[1].decode('utf8')
    players = int(PLAYERS_RE.match(players_raw).group('players'))
    return players

def main():
    player_last_seen = time.time()
    while True:
        time.sleep(10)

        players = get_players()
        LOGGER.info('{} players online'.format(players))

        if players is None:
            continue

        if players > 0:
            player_last_seen = time.time()
            continue

        seconds_since_player_last_seen = time.time() - player_last_seen
        LOGGER.info('{:.0f} seconds since last player seen'.format(seconds_since_player_last_seen))

        if seconds_since_player_last_seen >= GRACE_PERIOD:
            mark_instance_for_removal()
            break

if __name__ == "__main__":
    main()
