import logging
import os

import spot_tools.docker
import spot_tools.logger

spot_tools.logger.setup_logging()
LOGGER = logging.getLogger(__name__)

GAME = os.environ['GAME']


def get_instance(name = GAME):
    if not get_instance._container.get(name):
        get_instance._container[name] = spot_tools.docker.get_docker_client().containers.get(name)
    return get_instance._container[name]
get_instance._container = {}

def get_instance_health(name = GAME):
    return spot_tools.docker.get_docker_lowlevel_client().inspect_container(name)['State']['Health']['Status']
