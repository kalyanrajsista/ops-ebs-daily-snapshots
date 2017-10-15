# OPS
DevOps Housekeeping tasks. 

Overview: 

SNAPSHOT CREATION
-----------------
Create snapshots for EBS volume attached to EC2 instances. EC2 instances must be have name tags like 'Backup' 'Daily' or 'backup' 'daily'. Python script will match all the instances with the name tags and initiate the snapshot creation based on the CRON set as Cloudwatch event. This solution will scan EC2 instances across all regions in your AWS account.

SNAPSHOT CLEANUP
----------------
Cleans up snapshots based on RETENTION period to avoid costs for EBS storage. 

Also, if you have any Disaster Recovery AWS account, this solution will grant permission and copies the snapshot across AWS account. Currently, it is commented out in the script. To enable and make it work, specify the DR_ACCOUNT_ID as an environment variable in Lambda.

Environment Variables in AWS Lambda Function

1. DR_ACCOUNT_ID
2. SNAP_RETENTION

Step 1: Set Up the (Virtual) Environment

`virtualenv -p /usr/bin/python2.7 env`

`source env/bin/activate`

`pip install -r requirements.txt`

Step 2: Configure AWS CLI

Step 3: Attach IAM Policy
see policy.json

Step 4: Create a Distribution Folder

`cp -rf src dist`

`cp -rf env/lib/python2.7/site-packages/* dist`

Step 5: Zip

`cd path/to/dist`

`zip -r path/to/deployment_bundle.zip .`

`aws s3 cp path/to/ops-daily-snapshots.zip s3://bucket-name-lambdas`

`aws lambda update-function-code --function-name ops-daily-snapshots --s3-bucket bucket-name-lambdas --s3-key ops-daily-snapshots.zip --publish`

Step 6: Create an event (CRON) in Cloudwatch to trigger this lambda on desired need. For example: Hourly, Daily
