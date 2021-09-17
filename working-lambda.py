import json
import urllib.parse
from boto3 import client

DESIRED_STORAGE_CLASS = 'DEEP_ARCHIVE'
SIZE_THRESHOLD        = 128 * 1024

s3c = client('s3')

def lambda_handler(event, context):
#  print("Received event: " + json.dumps(event, indent=2))
  for i, record in enumerate(event['Records']):
  #    print("RECORD: " + json.dumps(record, indent=2))

    try:
      bucket = record['s3']['bucket']['name']
      key = urllib.parse.unquote_plus(record['s3']['object']['key'], encoding='utf-8')
      size = record['s3']['object']['size']
    except KeyError as e:
      print(f"{i} encountered while attempting to index s3 key: {record}")
      print(e)
      continue

    # assume that we are "chasing our own tail" if it's not a put- would be
    # better to figure out if there's a way to trace ourselves (maybe a tag, if
    # not too expensive to create and query? possibly database entry). The
    # insight here though is that Puts default to Standard, so those would be
    # the ones we'd want to act on.
    if record['eventName'] != 'ObjectCreated:Put':
      print(f"{i}: found a non-put event for object {key} ({size} bytes), not proceeding")
      continue

    if size > SIZE_THRESHOLD:
      print(f"***** record {i}, ARCHIVING: {key} {size}")

      try:
        s3c.copy({'Bucket': bucket, 'Key': key},
          bucket, key,
          ExtraArgs = {
            'StorageClass': DESIRED_STORAGE_CLASS,
            'MetadataDirective': 'COPY' })

      except Exception as e:
        print(e.__class__.__name__)
        print(e)
        print('if it\'s a permissions issue, try adding "s3:GetObject", "s3:GetObjectTagging", "s3:PutObject", "s3:PutObjectTagging"')

    else:
      # TODO: stick in database for later zip
      print(f"***** file {key} is {size} bytes, smaller than {SIZE_THRESHOLD}")
