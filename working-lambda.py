import json
import urllib.parse
from boto3 import client

DESIRED_STORAGE_CLASS = 'DEEP_ARCHIVE'
SIZE_THRESHOLD        = 128 * 1024

s3c = client('s3')

def lambda_handler(event, context):
#  print("Received event: " + json.dumps(event, indent=2))

  # Get the object from the event and show its content type
  for i, record in enumerate(event['Records']):
  #    print("RECORD: " + json.dumps(record, indent=2))
    # assume that we are "chasing our own tail" if it's a copy- would be better
    # to figure out if there's a way to trace ourselves
    if record['eventName'] == 'ObjectCreated:Copy':
      print(f"{i}: found an object copy event, not proceeding")
      continue

    try:
      bucket = record['s3']['bucket']['name']
      key = urllib.parse.unquote_plus(record['s3']['object']['key'], encoding='utf-8')
      size = record['s3']['object']['size']
    except KeyError as e:
      print(f"{i} encountered while attempting to index s3 key: {e}")
      continue

#    print(f"{i}: {size} {key} ({bucket})")

    if size > SIZE_THRESHOLD:
      print(f"***** record {i}, archiving file: {key} {size}")

      try:
        s3c.copy({'Bucket': bucket, 'Key': key},
          bucket, key,
          ExtraArgs = {
            'StorageClass': DESIRED_STORAGE_CLASS,
            'MetadataDirective': 'COPY' })

      except Exception as e:
        print(e.__class__.__name__)

      # TODO: fix these exception names?  Not sure why the logs weren't showing
      except InvalidObjectState as e:
        print("got called back on an object that is already moved to the desired storage class")

      except ClientError as e:
        print(e)
        print('if it\'s a permissions issue, try adding "s3:GetObject", "s3:GetObjectTagging", "s3:PutObject", "s3:PutObjectTagging"')

    else:
      # TODO: stick in database for later zip
      print(f"file {key} only {size} bytes, smaller than {SIZE_THRESHOLD}")
