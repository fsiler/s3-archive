#!/usr/bin/env python3
from boto3 import client
s3c = client("s3")

def changestorageclass(bucket, key, desiredclass='DEEP_ARCHIVE', noop=False):
  if noop:
    print(f"would've moved s3://{bucket}/{key} to {desiredclass}")
  else:
    s3c.copy({'Bucket': bucket, 'Key': key},
      bucket, key,
      ExtraArgs = {
        'StorageClass': desiredclass,
        'MetadataDirective': 'COPY' })
