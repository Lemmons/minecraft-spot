import json
import logging
import os
import os.path
import re
import tarfile
import tempfile
import time
import zipfile

import botocore.exceptions

import spot_tools.aws
import spot_tools.errors
import spot_tools.logger
import spot_tools.minecraft

spot_tools.logger.setup_logging()
LOGGER = logging.getLogger(__name__)

MINECRAFT_DATA = '/data'
BACKUP_INDEX_PATH = os.environ.get('BACKUP_INDEX_PATH', 'FeedTheBeast/backups/backups.json')
BACKUP_COMMAND = os.environ.get('BACKUP_COMMAND', 'rcon-cli ftb backup start')
BACKUPS_PATH = os.path.join(MINECRAFT_DATA, os.environ.get('BACKUPS_PATH', 'FeedTheBeast/backups'))
SAVE_RESTORE_PATH = os.path.join(MINECRAFT_DATA, 'FeedTheBeast')
BACKUP_S3_KEY = 'backups/latest.zip'
LEGACY_BACKUP_S3_KEY = 'backups/latest.tgz'
PREVIOUS_BACKUP_S3_KEY = 'backups/previous.zip'
OTHERS_BACKUP_S3_KEY = 'backups/others.tgz'
S3_BUCKET = os.environ.get('S3_BUCKET')

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

def get_legacy_s3_backup_time():
    return get_backup_time('legacy', LEGACY_BACKUP_S3_KEY)

def get_others_s3_backup_time():
    return get_backup_time('others', OTHERS_BACKUP_S3_KEY)

def local_backup():
    minecraft = spot_tools.minecraft.get_minecraft()
    if minecraft.status == "exited" or spot_tools.minecraft.get_minecraft_health() != "healthy":
        raise spot_tools.errors.UnableToBackupError("cannot backup, minecraft not running")

    LOGGER.info('backing-up minecraft locally')
    last_backup_time = get_latest_local_backup_time()
    minecraft.exec_run(BACKUP_COMMAND)
    count = 0
    while get_latest_local_backup_time() <= last_backup_time:
        time.sleep(1)
        count += 1
        if count > 60:
            LOGGER.warning('local backup taking more than 60 seconds. Timing out')
            return
    LOGGER.info('completed backing-up minecraft locally')

def local_backup_and_save_to_s3():
    local_backup()

    LOGGER.info('saving minecraft backup to s3')

    latest_backup = get_latest_local_backup()
    spot_tools.aws.save_to_s3(os.path.join(BACKUPS_PATH, latest_backup['file']), S3_BUCKET, BACKUP_S3_KEY)

    get_backup_time._time['latest'] = time.time()


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
    #             tar.add(MINECRAFT_DATA, filter=_filter)
    #
    #         spot_tools.aws.save_to_s3(file.name, OTHERS_BACKUP_S3_KEY)

def backup_if_needed():
    if (time.time() - get_latest_s3_backup_time()) > (20 * 60): # 20 minutes
        LOGGER.info('Last automatic s3 backup greater than 20 minute ago')
        local_backup_and_save_to_s3()

def restore_backup():
    # TODO: this is super jank and should be cleaned up
    try:
        minecraft = spot_tools.minecraft.get_minecraft()
        raise spot_tools.errors.UnableToRestoreError("Cannot restore backup when in state {}".format(minecraft.state))
    except spot_tools.errors.UnableToRestoreError:
        raise
    except:
        pass

    if get_legacy_s3_backup_time() and not get_latest_s3_backup_time():
        LOGGER.info('Restoring legacy backup from {}'.format(LEGACY_BACKUP_S3_KEY))
        filename = '/tmp/latest.tgz'
        LOGGER.info('Downloading {} to {}'.format(LEGACY_BACKUP_S3_KEY, filename))
        spot_tools.aws.download_from_s3(filename, S3_BUCKET, LEGACY_BACKUP_S3_KEY)
        with tarfile.open(name=filename, mode='r') as tar:
            LOGGER.info('Un-taring {} to {}'.format(filename, MINECRAFT_DATA))
            tar.extractall(MINECRAFT_DATA + '/..')
        return

    if get_others_s3_backup_time():
        LOGGER.info('Restoring backup of non-save minecraft dirs from {}'.format(OTHERS_BACKUP_S3_KEY))
        filename = '/tmp/other.tgz'
        LOGGER.info('Downloading {} to {}'.format(OTHERS_BACKUP_S3_KEY, filename))
        spot_tools.aws.download_from_s3(filename, S3_BUCKET, OTHERS_BACKUP_S3_KEY)
        with tarfile.open(name=filename, mode='r') as tar:
            LOGGER.info('Un-taring {} to {}'.format(filename, MINECRAFT_DATA))
            tar.extractall(MINECRAFT_DATA + '/..')

    if get_latest_s3_backup_time():
        LOGGER.info('Restoring backup from {}'.format(BACKUP_S3_KEY))
        filename = '/tmp/latest.zip'
        LOGGER.info('Downloading {} to {}'.format(BACKUP_S3_KEY, filename))
        spot_tools.aws.download_from_s3(filename, S3_BUCKET, BACKUP_S3_KEY)
        with zipfile.ZipFile(filename) as _zip:
            LOGGER.info('Un-zipping {} to {}'.format(filename, SAVE_RESTORE_PATH))
            _zip.extractall(SAVE_RESTORE_PATH)

        LOGGER.info('Saving previous backup to {}'.format(PREVIOUS_BACKUP_S3_KEY))
        spot_tools.aws.save_to_s3(filename, S3_BUCKET, PREVIOUS_BACKUP_S3_KEY)
