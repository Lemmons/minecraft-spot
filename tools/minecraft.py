import logging

import spot_tools.docker
import spot_tools.logger

spot_tools.logger.setup_logging()
LOGGER = logging.getLogger(__name__)

def get_minecraft():
    if not get_minecraft._container:
        get_minecraft._container = spot_tools.docker.get_docker_client().containers.get('minecraft')
    return get_minecraft._container
get_minecraft._container = None

def get_minecraft_health():
    return spot_tools.docker.get_docker_lowlevel_client().inspect_container('minecraft')['State']['Health']['Status']
