import os
import json
import boto3
import logging
s3 = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # Log the event for debugging purposes
    logger.info(event)

    try:
        for i in event['Records']:
            s3_event = json.loads(i['body'])

            for j in s3_event['Records']:
                bucket_name = j['s3']['bucket']['name']
                key = j['s3']['object']['key']
                event_name = j['eventName']
                basepath = "/mnt/efs"
                file_name = f"{basepath}/{os.path.basename(key)}"

                if event_name in ('ObjectCreated:Put', 'ObjectCreated:CompleteMultipartUpload'):
                    with open(file_name, 'wb') as f:
                        s3.download_fileobj(bucket_name, key, f)

                    # Test if download was successful
                    if os.path.exists(file_name):
                        logger.info(f"Downloaded file {key} to EFS")
                        logger.info(f"EFS files: {os.listdir(basepath)}")
                    else:
                        logger.error(f"Failed to download file {key} to EFS")

                elif event_name in ('ObjectRemoved:DeleteMarkerCreated', 'ObjectRemoved:Delete'):
                    if os.path.exists(file_name):
                        os.remove(file_name)
                        logger.info(f"Removed file {key} from EFS")
                    else:
                        logger.info(f"File not found in EFS: {key}")

    except Exception as exception:
        logger.exception(exception)
