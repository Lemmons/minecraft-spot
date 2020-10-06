import re

import spot_tools.instance
import spot_tools.factorio.rcon

PLAYERS_RE = re.compile(r'Players \((?P<players>\d*)\):.*')
def get_players():
    instance = spot_tools.instance.get_instance()
    if instance.status == "exited":
        return

    rcon = spot_tools.factorio.rcon.get_rcon_client()
    result = rcon.send_command('/players count')

    players = int(PLAYERS_RE.match(result).group('players'))

    return players
