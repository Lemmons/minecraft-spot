import json
import logging
import os
import os.path
import time
import zipfile

import spot_tools.aws
import spot_tools.backup
import spot_tools.errors
import spot_tools.instance
import spot_tools.logger
import spot_tools.factorio.rcon

spot_tools.logger.setup_logging()
LOGGER = logging.getLogger(__name__)

GAME_DATA = '/data'
BACKUPS_PATH = os.path.join(GAME_DATA, os.environ.get('BACKUPS_PATH', 'saves/'))
MOD_LIST = os.environ.get('MOD_LIST')
MODS_PATH = os.path.join(GAME_DATA, os.environ.get('MODS_PATH', 'mods/'))

S3_BUCKET = os.environ.get('S3_BUCKET')
BACKUP_S3_KEY = 'backups/latest.zip'
PREVIOUS_BACKUP_S3_KEY = 'backups/previous.zip'


def get_latest_local_backup():
    return {'time': get_latest_local_backup.time, 'file': get_latest_local_backup.file} 
get_latest_local_backup.time = None
get_latest_local_backup.file = None


def local_backup():
    instance = spot_tools.instance.get_instance()
    if instance.status == "exited":
        raise spot_tools.errors.UnableToBackupError("cannot backup, factorio not running")

    LOGGER.info('backing-up factorio locally')

    rcon = spot_tools.factorio.rcon.get_rcon_client()

    timestamp = int(time.time())
    rcon.send_command(f'/save {timestamp}.zip')

    path = f'{timestamp}.zip'

    full_path = os.path.join(BACKUPS_PATH, path)
    prev_size = -1
    size = 0
    while True:
        LOGGER.info(f'waiting for {full_path} to finish backup. size: {size}')
        try:
            size = os.stat(full_path).st_size
        except FileNotFoundError:
            LOGGER.warn(f'{full_path} not found')
            time.sleep(2)
            continue

        if size == prev_size:
            break

        prev_size = size
        time.sleep(2)

    get_latest_local_backup.time = timestamp
    get_latest_local_backup.file = path

    LOGGER.info('completed backing-up factorio locally')


def others_backup_if_needed():
    pass


def restore_backup():
    # TODO: this is super jank and should be cleaned up
    try:
        instance = spot_tools.instance.get_instance()
        raise spot_tools.errors.UnableToRestoreError("Cannot restore backup when in state {}".format(instance.state))
    except spot_tools.errors.UnableToRestoreError:
        raise
    except:
        pass

    if spot_tools.backup.get_latest_s3_backup_time():
        os.makedirs(BACKUPS_PATH, exist_ok=True)
        LOGGER.info('Restoring backup from {}'.format(BACKUP_S3_KEY))
        filename = os.path.join(BACKUPS_PATH, 'lastest.zip')
        LOGGER.info('Downloading {} to {}'.format(BACKUP_S3_KEY, filename))
        spot_tools.aws.download_from_s3(filename, S3_BUCKET, BACKUP_S3_KEY)
        LOGGER.info('Saving previous backup to {}'.format(PREVIOUS_BACKUP_S3_KEY))
        spot_tools.aws.save_to_s3(filename, S3_BUCKET, PREVIOUS_BACKUP_S3_KEY)

    _install_mods()

def _install_mods():
    os.makedirs(MODS_PATH, exist_ok=True)

    mod_list = list(filter(None,['base'] + MOD_LIST.split(',')))
    mods = {"mods": [{"name": mod_name, "enabled": "true"} for mod_name in mod_list]}

    mod_list_path = os.path.join(MODS_PATH, 'mod-list.json')
    LOGGER.info(f'Saving mod list: {mod_list} to path: {mod_list_path}')
    with open(mod_list_path, 'w') as fout:
        json.dump(mods, fout, indent=4)
