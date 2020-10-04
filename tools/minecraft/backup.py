import json
import logging
import os
import os.path
import re
import tarfile
import tempfile
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
BACKUP_INDEX_PATH = os.path.join(GAME_DATA, os.environ.get('BACKUP_INDEX_PATH', 'FeedTheBeast/local/ftbutilities/backups.json'))
BACKUP_COMMAND = os.environ.get('BACKUP_COMMAND', 'rcon-cli backup start')
SAVE_RESTORE_PATH = os.path.join(GAME_DATA, 'FeedTheBeast')

S3_BUCKET = os.environ.get('S3_BUCKET')
BACKUP_S3_KEY = 'backups/latest.zip'
LEGACY_BACKUP_S3_KEY = 'backups/latest.tgz'
PREVIOUS_BACKUP_S3_KEY = 'backups/previous.zip'
OTHERS_BACKUP_S3_KEY = 'backups/others.tgz'


def get_latest_local_backup():
    backups_index = BACKUP_INDEX_PATH

    backups = {backup['time']: backup for backup in json.load(open(backups_index)) if backup['success']==True}
    return backups[max(backups.keys())]

def get_latest_local_backup_time():
    try:
        backup = get_latest_local_backup()
        LOGGER.info('Last local backup was {} seconds ago'.format(time.time() - backup['time']/1000))
        return backup['time']/1000
    except (FileNotFoundError, ValueError) as e:
        LOGGER.warning('Could not find previous local backup')
        return 0

def get_legacy_s3_backup_time():
    return spot_tools.backup.get_backup_time('legacy', LEGACY_BACKUP_S3_KEY)

def get_others_s3_backup_time():
    return spot_tools.backup.get_backup_time('others', OTHERS_BACKUP_S3_KEY)

def local_backup():
    instance = spot_tools.instance.get_instance()
    if instance.status == "exited" or spot_tools.instance.get_instance_health() != "healthy":
        raise spot_tools.errors.UnableToBackupError("cannot backup, minecraft not running")

    LOGGER.info('backing-up minecraft locally')
    last_backup_time = get_latest_local_backup_time()
    instance.exec_run(BACKUP_COMMAND)
    count = 0
    while get_latest_local_backup_time() <= last_backup_time:
        time.sleep(1)
        count += 1
        if count > 60:
            LOGGER.warning('local backup taking more than 60 seconds. Timing out')
            return
    LOGGER.info('completed backing-up minecraft locally')


OTHERS_RE = re.compile(r'(.*\.zip)|(.*\.tgz)|(data/FeedTheBeast/world/.*)|(data/FeedTheBeast/backups/.*)')
def others_backup_if_needed():
    #### this still isn't working :(
    # with error FileNotFoundError: [Errno 2] No such file or directory: '/data/FeedTheBeast/OpenComputersMod-1.7.1.43-lua53-native.64.so'
    pass
    # def _filter(tar_info):
    #     if OTHERS_RE.match(tar_info.name):
    #         return None
    #     return tar_info
    # if not get_others_s3_backup_time():
    #     LOGGER.info('backing up non-save minecraft dirs')
    #     with tempfile.NamedTemporaryFile() as file:
    #         with tarfile.open(fileobj=file, mode='w:gz') as tar:
    #             tar.add(GAME_DATA, filter=_filter)
    #
    #         spot_tools.aws.save_to_s3(file.name, OTHERS_BACKUP_S3_KEY)


def restore_backup():
    # TODO: this is super jank and should be cleaned up
    try:
        instance = spot_tools.instance.get_instance()
        raise spot_tools.errors.UnableToRestoreError("Cannot restore backup when in state {}".format(instance.state))
    except spot_tools.errors.UnableToRestoreError:
        raise
    except:
        pass

    if get_legacy_s3_backup_time() and not spot_tools.backup.get_latest_s3_backup_time():
        LOGGER.info('Restoring legacy backup from {}'.format(LEGACY_BACKUP_S3_KEY))
        filename = '/tmp/latest.tgz'
        LOGGER.info('Downloading {} to {}'.format(LEGACY_BACKUP_S3_KEY, filename))
        spot_tools.aws.download_from_s3(filename, S3_BUCKET, LEGACY_BACKUP_S3_KEY)
        with tarfile.open(name=filename, mode='r') as tar:
            LOGGER.info('Un-taring {} to {}'.format(filename, GAME_DATA))
            tar.extractall(GAME_DATA + '/..')
        return

    if get_others_s3_backup_time():
        LOGGER.info('Restoring backup of non-save minecraft dirs from {}'.format(OTHERS_BACKUP_S3_KEY))
        filename = '/tmp/other.tgz'
        LOGGER.info('Downloading {} to {}'.format(OTHERS_BACKUP_S3_KEY, filename))
        spot_tools.aws.download_from_s3(filename, S3_BUCKET, OTHERS_BACKUP_S3_KEY)
        with tarfile.open(name=filename, mode='r') as tar:
            LOGGER.info('Un-taring {} to {}'.format(filename, GAME_DATA))
            tar.extractall(GAME_DATA + '/..')

    if spot_tools.backup.get_latest_s3_backup_time():
        LOGGER.info('Restoring backup from {}'.format(BACKUP_S3_KEY))
        filename = '/tmp/latest.zip'
        LOGGER.info('Downloading {} to {}'.format(BACKUP_S3_KEY, filename))
        spot_tools.aws.download_from_s3(filename, S3_BUCKET, BACKUP_S3_KEY)
        with zipfile.ZipFile(filename) as _zip:
            LOGGER.info('Un-zipping {} to {}'.format(filename, SAVE_RESTORE_PATH))
            _zip.extractall(SAVE_RESTORE_PATH)

        LOGGER.info('Saving previous backup to {}'.format(PREVIOUS_BACKUP_S3_KEY))
        spot_tools.aws.save_to_s3(filename, S3_BUCKET, PREVIOUS_BACKUP_S3_KEY)
