import json
import os
import os.path
import time
import zipfile

import spot_tools.aws
import spot_tools.errors
import spot_tools.logger
import spot_tools.minecraft

spot_tools.logger.setup_logging()
LOGGER = logging.getLogger(__name__)

MINECRAFT_DATA = '/data'
BACKUPS_PATH = os.path.join(MINECRAFT_DATA, 'FeedTheBeast/backups')
BACKUP_S3_KEY = 'backups/latest.zip'
# BACKUP_S3_KEY = 'backups/latest.tgz'
PREVIOUS_BACKUP_S3_KEY = 'backups/previous.zip'
S3_BUCKET = os.environ.get('S3_BUCKET')

def get_latest_local_backup():
    backups_index = os.path.join(BACKUPS_PATH, 'backups.json')

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

def get_latest_s3_backup_time():
    if not get_latest_s3_backup_time.time:
        client = spot_tools.aws.get_boto_client('s3')
        response = client.head_object(Bucket=S3_BUCKET, Key=BACKUP_S3_KEY)
        get_latest_s3_backup_time.time = response['LastModified'].timestamp()
        # need to catch the case where this file doesn't exist
    LOGGER.info('Last s3 backup was {} seconds ago'.format(time.time() - get_latest_s3_backup_time.time))
    return get_latest_s3_backup_time._time
get_latest_s3_backup_time._time = None

def local_backup():
    minecraft = spot_tools.minecraft.get_minecraft()
    if minecraft.status == "exited" or spot_tools.minecraft.get_minecraft_health() != "healthy":
        raise "cannot backup, minecraft not running"

    LOGGER.info('backing-up minecraft locally')
    last_backup_time = get_latest_local_backup_time()
    minecraft.exec_run('rcon-cli ftb backup start')
    count = 0
    while get_latest_local_backup_time() <= last_backup_time:
        sleep(1)
        count += 1
        if count > 60:
            LOGGER.warning('local backup taking more than 60 seconds. Timing out')
            return
    LOGGER.info('completed backing-up minecraft locally')

def local_backup_and_save_to_s3():
    #TODO: maybe also gzip and upload the rest of the folder (excluding backups and saves)
    local_backup()

    LOGGER.info('saving minecraft backup to s3')

    latest_backup = get_latest_local_backup()
    spot_tools.aws.save_to_s3(os.path.join(BACKUPS_PATH, latest_backup['file']), S3_BUCKET, BACKUP_S3_KEY)

    get_latest_s3_backup_time._time = time.time()

def others_backup_if_needed():
    #### this should only happen if backups/others.tgz doesn't already exist in s3 (never was made or recently was deleted)
    # LOGGER.info('backing up minecraft')
    # key = "backups/others.tgz"
    # with tempfile.NamedTemporaryFile() as file:
    #     with tarfile.open(fileobj=file, mode='w:gz') as tar:
            # tar.add(MINECRAFT_DATA,
            #     excludes=[
            #         '*.zip',
            #         'FeedTheBeast/world',
            #         'FeedTheBeast/backups',
            #     ]
            # )

    #         save_to_s3(file.name, key)

def backup_if_needed():
    if (time.time() - get_latest_s3_backup_time()) > (20 * 60): # 20 minutes
        LOGGER.info('Last automatic s3 backup greater than 20 minute ago')
        local_backup_and_save_to_s3()

def restore_backup():
    # TODO: this is super jank and should be cleaned up
    try:
        minecraft = spot_tools.minecraft.get_minecraft()
        raise spot_tools.UnableToRestoreError("Cannot restore backup when in state {}".format(minecraft.state))
    except spot_tools.UnableToRestoreError:
        raise
    except:
        pass

    #### restore others (main mod contents) if exists
    # key = "backups/others.tgz"
    # LOGGER.info('Restoring backup from {}'.format(key))
    # with tempfile.NamedTemporaryFile() as file:
    #     LOGGER.info('Downloading {} to {}'.format(key_latest, file.name))
    #     client.download_fileobj(S3_BUCKET, key_latest, file)
    #     with tarfile.open(name=file.name, mode='r') as tar:
    #         LOGGER.info('Un-taring {} to {}'.format(file.name, MINECRAFT_DATA))
    #         tar.extractall(MINECRAFT_DATA + '/..')

    LOGGER.info('Restoring backup from {}'.format(BACKUP_S3_KEY))

    filename = '/tmp/latest.zip'
    LOGGER.info('Downloading {} to {}'.format(BACKUP_S3_KEY, filename))
    spot_tools.aws.download_from_s3(filename, S3_BUCKET, BACKUP_S3_KEY)

    with zipfile.ZipFile(filename) as _zip:
        world_path = os.path.join(MINECRAFT_DATA, 'FeedTheBeast/world/') # not sure if this is the correct location
        LOGGER.info('Un-zipping {} to {}'.format(filename, world_path))
        _zip.extractall(world_path)

    LOGGER.info('Saving previous backup to {}'.format(PREVIOUS_BACKUP_S3_KEY))
    spot_tool.aws.save_to_s3(filename, S3_BUCKET, PREVIOUS_BACKUP_S3_KEY)
