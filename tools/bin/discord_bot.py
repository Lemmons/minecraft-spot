#!/usr/bin/env python3

import spot_tools.logger
import spot_tools.discord

spot_tools.logger.setup_logging()
LOGGER = logging.getLogger(__name__)

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

def main():
    if DISCORD_TOKEN:
        LOGGER.warning('Discord bot starting')
        spot_tools.discord.client.run(DISCORD_TOKEN)
    else:
        LOGGER.warning('No discord token provided. Bot not running')
        while True:
            time.sleep(600)
