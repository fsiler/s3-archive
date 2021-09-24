#!/usr/bin/env python3
from boto3 import client, resource
from urllib.parse import unquote_plus
import json

DESIRED_STORAGE_CLASS = 'DEEP_ARCHIVE'
SIZE_THRESHOLD        = 128 * 1024

s3c = client('s3')
s3r = resource('s3')

def lambda_handler(event, context):
  for i, record in enumerate(event['Records']):
    try:
      bucket = record['s3']['bucket']['name']
      key    = unquote_plus(record['s3']['object']['key'], encoding='utf-8')
      size   = record['s3']['object']['size']
    except KeyError as e:
      print(f"{i} encountered while attempting to index s3 key: {record}")
      print(e)
      continue

    o = s3r.ObjectSummary(bucket, key)

    if size > SIZE_THRESHOLD and o.storage_class != DESIRED_STORAGE_CLASS:
      print(f"***** record {i}, ARCHIVING: {key} {size}")

      try:
        s3c.copy({'Bucket': bucket, 'Key': key},
          bucket, key,
          ExtraArgs = {
            'StorageClass': DESIRED_STORAGE_CLASS,
            'MetadataDirective': 'COPY' })

      except Exception as e:
        print("error on copy:")
        print(e.__class__.__name__)
        print(e)
        print('if it\'s a permissions issue, try adding "s3:GetObject", "s3:GetObjectTagging", "s3:PutObject", "s3:PutObjectTagging"')

    else:
      print(f"***** no action with object {key}, {size} bytes in class {o.storage_class}")
