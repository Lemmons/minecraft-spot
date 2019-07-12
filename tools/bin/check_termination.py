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


def stop_and_backup_minecraft():
    spot_tools.backup.local_backup_and_save_to_s3()

    LOGGER.info('stopping minecraft')
    minecraft = spot_tools.minecraft.get_minecraft()

    if minecraft.status != "exited":
        minecraft.exec_run('rcon-cli stop')

    spot_tools.backup.others_backup_if_needed()


def main():
    terminate = False
    while not terminate:
        terminate = spot_tools.aws.check_termination(stop_and_backup_minecraft)
        LOGGER.debug('Waiting for termination')
        time.sleep(1)

if __name__ == "__main__":
    main()
