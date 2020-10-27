import re

import factorio_rcon.factorio_rcon

import spot_tools.instance
import spot_tools.factorio.rcon

PLAYERS_RE = re.compile(r'Online players \((?P<players>\d*)\):.*')
def get_players():
    instance = spot_tools.instance.get_instance()
    if instance.status == "exited":
        return

    try:
        rcon = spot_tools.factorio.rcon.get_rcon_client()
        result = rcon.send_command('/players online')
    except (factorio_rcon.factorio_rcon.RCONClosed, factorio_rcon.factorio_rcon.RCONConnectError):
        # reset the rcon client if we loose it
        spot_tools.factorio.rcon.get_rcon_client._client = None
        return None

    players = int(PLAYERS_RE.match(result).group('players'))

    return players
