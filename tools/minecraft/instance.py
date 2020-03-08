import logging
import os

import spot_tools.logger
import spot_tools.instance

spot_tools.logger.setup_logging()
LOGGER = logging.getLogger(__name__)


def stop():
    instance = spot_tools.instance.get_instance()
    instance.exec_run('rcon-cli stop')
