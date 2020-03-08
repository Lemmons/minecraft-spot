#!/usr/bin/env python3

import importlib
import logging
import os
import time

import requests

import spot_tools.aws
import spot_tools.backup
import spot_tools.logger
import spot_tools.instance

spot_tools.logger.setup_logging()
LOGGER = logging.getLogger(__name__)

# dynamic import based on running game, currently supports minecraft or factorio
GAME = os.environ['GAME']
game_instance = importlib.import_module(f'spot_tools.{GAME}.instance')


def stop_and_backup():
    spot_tools.backup.local_backup_and_save_to_s3()

    LOGGER.info(f'stopping {GAME}')
    instance = spot_tools.instance.get_instance()

    if instance.status != "exited":
        game_instance.stop()

    spot_tools.backup.others_backup_if_needed()


def main():
    terminate = False
    while not terminate:
        terminate = spot_tools.aws.check_termination(stop_and_backup)
        LOGGER.debug('Waiting for termination')
        time.sleep(1)


if __name__ == "__main__":
    main()
