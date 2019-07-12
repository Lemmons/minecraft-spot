#!/usr/bin/env python3

import logging
import os
import time
import re

import requests

import spot_tools.aws
import spot_tools.logger
import spot_tools.minecraft

spot_tools.logger.setup_logging()
LOGGER = logging.getLogger(__name__)

GRACE_PERIOD = int(os.environ['GRACE_PERIOD'])

PLAYERS_RE = re.compile(r'There are (?P<players>\d*)/\d* players online:')
def get_players():
    minecraft = spot_tools.minecraft.get_minecraft()
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
            spot_tools.aws.mark_instance_for_removal()
            break

if __name__ == "__main__":
    main()
