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
    if event['headers'].get('Authorization'):
        del event['headers']['Authorization']
    return event

def is_authorized(scope, method):
    if not scope:
        LOGGER.info('No scopes found')
        return False

    scopes = scope.split(' ')
    authorized_scope = '{}:server'.format(method)

    if authorized_scope in scopes:
        LOGGER.info('Authorized: %s found in %s', authorized_scope, scopes)
        return True
    LOGGER.info('Unauthorized: %s not in %s', authorized_scope, scopes)
    return False

def method_base(event, method):
    remove_sensitive_headers(event)
    LOGGER.info('Event: %s', event)
    LOGGER.info('Authorization Scopes: %s', event['requestContext']['authorizer'].get('scope'))
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

RUNNING_STATES = ['InService']
STARTING_STATES = ['Pending', 'Pending:Wait', 'Pending:Proceed']
STOPPING_STATES = ['Terminating', 'Terminating:Proceed']
def status(event, context):
    try:
        method_base(event, 'status')
    except Unauthorized:
        return generate_response_with_cors(event, body='Unauthorized', status_code=401)

    LOGGER.info('Getting server status')

    client = boto3.client('autoscaling')
    group = client.describe_auto_scaling_groups(AutoScalingGroupNames=[os.environ['GROUP_NAME']])['AutoScalingGroups'][0]

    body = {}

    launch_config_name = group['LaunchConfigurationName']
    body['desired_capacity'] = group['DesiredCapacity']

    # TODO: add latest backups name/date

    starting_instances = [instance for instance in group['Instances'] if instance['LifecycleState'] in STARTING_STATES]
    running_instances = [instance for instance in group['Instances'] if instance['LifecycleState'] in RUNNING_STATES]
    stopping_instances = [instance for instance in group['Instances'] if instance['LifecycleState'] in STOPPING_STATES]

    if starting_instances:
        body['status'] = 'Starting'
    elif running_instances:
        body['status'] = 'Running'
    elif stopping_instances:
        body['status'] = 'Stopping'
    else:
        body['status'] = 'Stopped'

    if body['status'] != 'Running':
        return generate_response_with_cors(event, json.dumps(body))

    # TODO: get minecraft status from server and add it to the stats
    return generate_response_with_cors(event, json.dumps(body))

def cors(event, context):
    remove_sensitive_headers(event)
    LOGGER.info('Event: %s', event)
    return generate_response_with_cors(event,
        headers={
            "Access-Control-Allow-Headers" : os.environ.get('CORS_HEADERS'),
            "Access-Control-Allow-Methods" : os.environ.get('CORS_METHODS'),
        }
    )
