import asyncio
import importlib
import logging
import os
import re

import discord

import spot_tools.instance
import spot_tools.logger
import spot_tools.aws

GAME = os.environ['GAME']
game_players = importlib.import_module(f'spot_tools.{GAME}.players')

spot_tools.logger.setup_logging()
LOGGER = logging.getLogger(__name__)

COMMAND_RE = re.compile(r'^!(?P<phrase>(hey )?puter|game|server)( (?P<command>.+)|.*)$')

DISCORD_CHANNEL = os.environ.get('DISCORD_CHANNEL')
DISCORD_SERVER = os.environ.get('DISCORD_SERVER')
FQDN = os.environ.get('FQDN')

client = discord.Client()

async def send_server_status():
    await client.wait_until_ready()
    channel = discord.utils.get(client.get_all_channels(), guild__name=DISCORD_SERVER, name=DISCORD_CHANNEL)
    status = None
    while not client.is_closed:
        if status is None:
            await channel.send(f'{GAME} server is starting')
            status = 'starting'

        if status == 'starting':
            try:
                players = game_players.get_players()
            except:
                players = None
            if players is not None:
                ip_address = spot_tools.aws.get_ip_address()
                await channel.send(f'{GAME} server is up at: {FQDN} ({ip_address})')
                return
        await asyncio.sleep(10)

client.loop.create_task(send_server_status())

@client.event
async def on_ready():
    LOGGER.info(f'Discord bot started as {client.user}')

@client.event
async def on_message(message):
    LOGGER.debug(f'received message: {message.content}')

    if message.author == client.user:
        return

    match = COMMAND_RE.match(message.content)
    if not match:
        LOGGER.debug(f'no match found in: {message.content}')
        return

    command = match.groupdict().get('command', 'help')
    if command == 'players':
        try:
            players = game_players.get_players()
        except:
            players = None

        if players is None:
            await message.channel.send('No response: server is either starting up or shutting down.')
        else:
            await message.channel.send(f'{players} player(s) online')

    elif command in ['stop', 'shutdown']:
        await message.channel.send('Beginning server shutdown')
        spot_tools.aws.mark_instance_for_removal()

    elif command == 'help':
        await message.channel.send('''
            Valid commands are:
            players - get number of players on server
            shutdown - shutdown the server
            stop - alias for shutdown
        ''')
