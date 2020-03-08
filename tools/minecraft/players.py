#!/usr/bin/env python3

import logging
import re
import importlib

import spot_tools.aws
import spot_tools.logger
import spot_tools.instance

spot_tools.logger.setup_logging()
LOGGER = logging.getLogger(__name__)

PLAYERS_RE = re.compile(r'There are (?P<players>\d*)/\d* players online:')
def get_players():
    instance = spot_tools.instance.get_instance()
    if instance.status == "exited":
        return

    result = instance.exec_run('rcon-cli list')
    if result[0] != 0:
        return
    players_raw = result[1].decode('utf8')
    players = int(PLAYERS_RE.match(players_raw).group('players'))
    return players
