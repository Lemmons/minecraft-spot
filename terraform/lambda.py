import os

import boto3

PASSPHRASE = os.environ.get('PASSPHRASE', 'abracadabra')

def start(event, context):
    if not event['queryStringParameters'] or event['queryStringParameters'].get('magic_word') != PASSPHRASE:
        return {
            "statusCode": 403,
            "headers": {"Content-Type": "application/json"},
            "body": "Unauthorized"
        }

    client = boto3.client('autoscaling')
    client.set_desired_capacity(
        AutoScalingGroupName=os.environ['GROUP_NAME'],
        DesiredCapacity=1,
        HonorCooldown=False,
    )
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": "starting"
    }

def stop(event, context):
    if not event['queryStringParameters'] or event['queryStringParameters'].get('magic_word') != PASSPHRASE:
        return {
            "statusCode": 403,
            "headers": {"Content-Type": "application/json"},
            "body": "Unauthorized"
        }

    client = boto3.client('autoscaling')
    client.set_desired_capacity(
        AutoScalingGroupName=os.environ['GROUP_NAME'],
        DesiredCapacity=0,
        HonorCooldown=False,
    )
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": "stopping"
    }
