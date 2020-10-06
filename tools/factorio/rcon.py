import os

import factorio_rcon

GAME_DATA = '/data'

def get_rcon_client():
    if not get_rcon_client._client:
        with open(os.path.join(GAME_DATA, 'config/rconpw'), 'r') as fin:
                rconpw = fin.read()
        get_rcon_client._client = factorio_rcon.RCONClient("factorio", 27015, rconpw)
    return get_rcon_client._client
get_rcon_client._client = None
