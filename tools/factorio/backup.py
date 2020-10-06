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

S3_BUCKET = os.environ.get('S3_BUCKET')
BACKUP_S3_KEY = 'backups/latest.zip'
PREVIOUS_BACKUP_S3_KEY = 'backups/previous.zip'


def get_latest_local_backup():
    return {'time': get_latest_local_backup.time, 'file': get_latest_local_backup.file} 
get_latest_local_backup.time = None
get_latest_local_backup.file = None


def local_backup():
    instance = spot_tools.instance.get_instance()
    if instance.status == "exited" or spot_tools.instance.get_instance_health() != "healthy":
        raise spot_tools.errors.UnableToBackupError("cannot backup, factorio not running")

    LOGGER.info('backing-up factorio locally')

    rcon = spot_tools.factorio.rcon.get_rcon_client()

    timestamp = int(time.time())
    rcon.send_command(f'/save {timestamp}.zip')

    path = os.path.join(BACKUPS_PATH, f'{timestamp}.zip')

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
        LOGGER.info('Restoring backup from {}'.format(BACKUP_S3_KEY))
        filename = os.join(BACKUPS_PATH, 'lastest.zip')
        LOGGER.info('Downloading {} to {}'.format(BACKUP_S3_KEY, filename))
        spot_tools.aws.download_from_s3(filename, S3_BUCKET, BACKUP_S3_KEY)
        LOGGER.info('Saving previous backup to {}'.format(PREVIOUS_BACKUP_S3_KEY))
        spot_tools.aws.save_to_s3(filename, S3_BUCKET, PREVIOUS_BACKUP_S3_KEY)