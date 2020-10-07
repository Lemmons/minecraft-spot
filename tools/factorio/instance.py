import spot_tools.factorio.rcon

def stop():
    rcon = spot_tools.factorio.rcon.get_rcon_client()
    rcon.send_command('/quit')
