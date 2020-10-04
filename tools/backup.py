import importlib
import logging
import os
import os.path
import time

import botocore.exceptions

import spot_tools.aws
import spot_tools.logger

# dynamic import based on running game, currently supports minecraft or factorio
GAME = os.environ['GAME']
game_backup = importlib.import_module(f'spot_tools.{GAME}.backup')

spot_tools.logger.setup_logging()
LOGGER = logging.getLogger(__name__)

GAME_DATA = '/data'
BACKUPS_PATH = os.path.join(GAME_DATA, os.environ.get('BACKUPS_PATH'))
S3_BUCKET = os.environ.get('S3_BUCKET')
BACKUP_S3_KEY = 'backups/latest.zip'


def get_latest_local_backup():
    return game_backup.get_latest_local_backup()


def get_backup_time(backup_type, key):
    if get_backup_time._time.get(backup_type) is None:
        client = spot_tools.aws.get_boto_client('s3')
        try:
            response = client.head_object(Bucket=S3_BUCKET, Key=key)
            get_backup_time._time[backup_type] = response['LastModified'].timestamp()
        except botocore.exceptions.ClientError as e:
            if int(e.response['Error']['Code']) == 404:
                get_backup_time._time[backup_type] = 0
                LOGGER.warning('{} never backed up to s3'.format(backup_type))
                return get_backup_time._time[backup_type]
            raise
    LOGGER.debug('Last {} s3 backup was {} seconds ago'.format(backup_type, time.time() - get_backup_time._time[backup_type]))
    return get_backup_time._time[backup_type]
get_backup_time._time = {}

def get_latest_s3_backup_time():
    return get_backup_time('latest', BACKUP_S3_KEY)

def local_backup():
    game_backup.local_backup()

def local_backup_and_save_to_s3():
    local_backup()

    LOGGER.info(f'saving {GAME} backup to s3')

    latest_backup = get_latest_local_backup()
    spot_tools.aws.save_to_s3(os.path.join(BACKUPS_PATH, latest_backup['file']), S3_BUCKET, BACKUP_S3_KEY)

    get_backup_time._time['latest'] = time.time()

def backup_if_needed():
    if (time.time() - get_latest_s3_backup_time()) > (20 * 60): # 20 minutes
        LOGGER.info('Last automatic s3 backup greater than 20 minute ago')
        local_backup_and_save_to_s3()

def restore_backup():
    game_backup.restore_backup()
