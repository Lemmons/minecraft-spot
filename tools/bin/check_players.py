#!/usr/bin/env python3

import importlib
import logging
import os
import time
import re

import spot_tools.aws
import spot_tools.logger

# dynamic import based on running game, currently supports minecraft or factorio
GAME = os.environ['GAME']
game_players = importlib.import_module(f'spot_tools.{GAME}.players')

spot_tools.logger.setup_logging()
LOGGER = logging.getLogger(__name__)

GRACE_PERIOD = int(os.environ['GRACE_PERIOD'])

def main():
    player_last_seen = time.time()
    while True:
        time.sleep(10)

        players = game_players.get_players()
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
