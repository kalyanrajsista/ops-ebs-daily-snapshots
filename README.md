# OPS
DevOps Housekeeping tasks

Step 1: Set Up the (Virtual) Environment
virtualenv -p /usr/bin/python2.7 env
source env/bin/activate
pip install -r requirements.txt

Step 2: Configure AWS CLI

Step 3: Attach IAM Policy
see policy.json

Step 4: Create a Distribution Folder
cp -rf src dist

cp -rf env/lib/python2.7/site-packages/* dist

Step 5: Zip
cd path/to/dist
zip -r path/to/deployment_bundle.zip .

aws s3 cp path/to/ops-daily-snapshots.zip s3://bucket-name-lambdas

aws lambda update-function-code --function-name ops-daily-snapshots --s3-bucket bucket-name-lambdas --s3-key ops-daily-snapshots.zip --publish
