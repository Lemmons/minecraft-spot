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

spot_tools.logger.setup_logging()
LOGGER = logging.getLogger(__name__)

GAME_DATA = '/data'
BACKUPS_PATH = os.path.join(GAME_DATA, os.environ.get('BACKUPS_PATH', 'backups/'))
WORLD_PATH = os.path.join(GAME_DATA, os.environ.get('WORLD_PATH', 'world/'))

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
        raise spot_tools.errors.UnableToBackupError("cannot backup, minecraft not running")

    LOGGER.info('backing-up minecraft locally')

    instance.exec_run('rcon-cli save-off')
    instance.exec_run('rcon-cli save-all')

    # create path if it doesn't exist
    os.makedirs(BACKUPS_PATH, exist_ok=True)

    timestamp = int(time.time())
    path = os.path.join(BACKUPS_PATH, f'{timestamp}.zip')
    with zipfile.ZipFile(path, 'w') as backup:
       for root, _, files in os.walk(WORLD_PATH):
           for _file in files:
               full_path = os.path.join(root, _file)
               backup.write(
                   full_path,
                   arcname=os.path.relpath(
                       full_path,
                       start=WORLD_PATH))

    instance.exec_run('rcon-cli save-on')
    get_latest_local_backup.time = timestamp
    get_latest_local_backup.file = path

    LOGGER.info('completed backing-up minecraft locally')


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
        filename = '/tmp/latest.zip'
        LOGGER.info('Downloading {} to {}'.format(BACKUP_S3_KEY, filename))
        spot_tools.aws.download_from_s3(filename, S3_BUCKET, BACKUP_S3_KEY)
        with zipfile.ZipFile(filename) as _zip:
            LOGGER.info('Un-zipping {} to {}'.format(filename, WORLD_PATH))
            _zip.extractall(WORLD_PATH)

        LOGGER.info('Saving previous backup to {}'.format(PREVIOUS_BACKUP_S3_KEY))
        spot_tools.aws.save_to_s3(filename, S3_BUCKET, PREVIOUS_BACKUP_S3_KEY)
