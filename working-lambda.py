#!/usr/bin/env python3
from boto3 import client, resource
from json import dumps
from urllib.parse import unquote_plus

DESIRED_STORAGE_CLASS = 'DEEP_ARCHIVE'
SIZE_THRESHOLD        = 128 * 1024

s3c = client('s3')
s3r = resource('s3')

def lambda_handler(event, context):
  """archives objects larger than THRESHOLD.  Needs permissions "s3:GetObject", "s3:GetObjectTagging", "s3:PutObject", "s3:PutObjectTagging"'"""
  for i, record in enumerate(event['Records']):
    try:
      bucket = record['s3']['bucket']['name']
      key    = unquote_plus(record['s3']['object']['key'], encoding='utf-8')
      size   = record['s3']['object']['size']
    except KeyError as e:
      print(f"{i} encountered while attempting to index s3 key: {record}- maybe I was given a non-s3 event?")
      print(e)
      continue

    o = s3r.ObjectSummary(bucket, key)
    print(f"got event {record.get('eventName')} for key {key} in bucket {bucket} ({size} bytes), storage class {o.storage_class}: ", end="")

    if size > SIZE_THRESHOLD and o.storage_class != DESIRED_STORAGE_CLASS:
      print(f"ARCHIVING")

      s3c.copy({'Bucket': bucket, 'Key': key},
        bucket, key,
        ExtraArgs = {
          'StorageClass': DESIRED_STORAGE_CLASS,
          'MetadataDirective': 'COPY' })

    else:
      print(f"no action")
