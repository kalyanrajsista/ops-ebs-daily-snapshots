import boto3
import datetime
import logging
import os
from botocore.exceptions import ClientError
from pytz import timezone

from logger import Logger

logger = Logger()

ec2 = boto3.client('ec2')
iam = boto3.client('iam')

def take_snapshots():
    reservations = ec2.describe_instances(
        Filters=[
            {'Name': 'tag-key', 'Values': ['backup', 'Backup']},
            {'Name': 'tag-value', 'Values': ['daily', 'Daily']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    ).get(
        'Reservations', []
    )

    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])

    logger.info('Found {0} instances that need backing up'.format(len(instances)))

    for instance in instances:
        name_tags = [x for x in instance['Tags'] if x['Key'] == 'Name']
        instance_name = 'none'

        if name_tags:
            instance_name = name_tags[0]['Value']
            logger.info('instance name {0}'.format(instance_name))

        for dev in instance['BlockDeviceMappings']:

            if dev.get('Ebs', None) is None:
                logger.info('ebs None')
                continue

            if dev['Ebs']['DeleteOnTermination'] == True:
                continue

            logger.info('Taking the snapshot now')

            vol_id = dev['Ebs']['VolumeId']
            timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S-UTC')
            description = 'snapshot-{0}-{1}'.format(timestamp, instance_name)
            logger.info('Found EBS volume {0} on instance {1}'.format(
                vol_id, instance['InstanceId']))

            try:
                snapshot_id = ec2.create_snapshot(VolumeId=vol_id, Description=description)['SnapshotId']
                logger.info('Created snapshot {0}'.format(snapshot_id))
                ec2.create_tags(
                    Resources=[snapshot_id],
                    Tags=[
                        {
                            'Key': 'Backup',
                            'Value': 'Daily'
                        },
                    ]
                )

                logger.info('Created snapshot {0}'.format(description))

                #dr_account_id = os.environ.get('DR_ACCOUNT_ID', None)
                #if dr_account_id:
                #    ec2.modify_snapshot_attribute(
                #        Attribute='createVolumePermission',
                #        OperationType='add',
                #        SnapshotId=snapshot_id,
                #        UserIds=[dr_account_id]
                #    )
                #
                #    logger.info('Assigned snapshot permission to DR account: {0}'.format(snapshot_id))
                #else:
                #    logger.warning('DR account number not provided--no permissions added!')

            except ClientError as e:
                logger.error('Problem encountered while taking snapshot: {0}'.format(e))


def cleanup_snapshots():
    current_date = datetime.datetime.utcnow().replace(tzinfo=timezone('UTC'))
    retention_days = os.environ.get('SNAP_RETENTION', 14)
    logger.info("Cleanup with rentention days = {0}".format(retention_days))

    account_id = iam.get_user(UserName='housekeeping')['User']['Arn'].split(':')[4]
    logger.info("Using account id {0}".format(account_id))

    results = ec2.describe_snapshots(
        OwnerIds=[account_id],
        Filters=[
            {'Name': 'tag-key', 'Values': ['backup', 'Backup']},
            {'Name': 'status', 'Values': ['completed']},
        ]
    )
    for snapshot in results['Snapshots']:
        start_date = snapshot['StartTime']
        snapshot_id = snapshot['SnapshotId']
        if (current_date - start_date).days > retention_days:
            logger.info("Deleting old snapshot {0}".format(snapshot_id))
            ec2.delete_snapshot(
                SnapshotId=snapshot_id
            )

def lambda_handler(event, context):
	take_snapshots()
	#cleanup_snapshots()


# Uncomment to test at the command-line
lambda_handler(None, None)
