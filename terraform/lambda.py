import json
import logging
import os

import boto3


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class Unauthorized(Exception):
    pass


def get_cors_origin(headers):
    hostname = headers.get('origin') or headers.get('Host')
    origins = os.environ.get('CORS_ORIGINS').split(',')
    if hostname in origins:
        return "{}".format(hostname)
    else:
        return "{}".format(origins[0])

def generate_response_with_cors(event, body=None, headers=None, status_code=200):
    response = {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "headers" : {
            "Access-Control-Allow-Origin"  : get_cors_origin(event['headers']),
        }
    }

    if headers:
        response['headers'].update(headers)

    if body:
        response['body'] = body

    return response

def remove_sensitive_headers(event):
    del event['headers']['Authorization']
    return event

def is_authorized(scope, method):
    if not scope:
        return False

    scopes = scope.split(' ')
    if '{}:server' in scopes:
        return True
    return False

def method_base(event, method):
    remove_sensitive_headers(event)
    LOGGER.info('Event: %s', event)
    LOGGER.info('Authorization Scopes: %s', event['requestContext']['authorizer']['scope'])
    if not is_authorized(event['requestContext']['authorizer'].get('scope'), method):
        raise Unauthorized


def start(event, context):
    try:
        method_base(event, 'start')
    except Unauthorized:
        return generate_response_with_cors(event, body='Unauthorized', status_code=401)

    LOGGER.info('Starting server. Setting instance count to 1.')

    client = boto3.client('autoscaling')
    client.set_desired_capacity(
        AutoScalingGroupName=os.environ['GROUP_NAME'],
        DesiredCapacity=1,
        HonorCooldown=False,
    )
    return generate_response_with_cors(event, "starting")

def stop(event, context):
    try:
        method_base(event, 'stop')
    except Unauthorized:
        return generate_response_with_cors(event, body='Unauthorized', status_code=401)

    LOGGER.info('Stopping server. Setting instance count to 0.')

    client = boto3.client('autoscaling')
    client.set_desired_capacity(
        AutoScalingGroupName=os.environ['GROUP_NAME'],
        DesiredCapacity=0,
        HonorCooldown=False,
    )
    return generate_response_with_cors(event, "stopping")

def cors(event, context):
    remove_sensitive_headers(event)
    LOGGER.info('Event: %s', event)
    return generate_response_with_cors(event,
        headers={
            "Access-Control-Allow-Headers" : os.environ.get('CORS_HEADERS'),
            "Access-Control-Allow-Methods" : os.environ.get('CORS_METHODS'),
        }
    )
