#!/usr/bin/env python3
from boto3 import resource, client
s3c = client('s3')    # low level
s3r = resource('s3')  # high level

BUCKET = 'fms-python-glacier-test'
KEY    = 'MakeMKV_log.txt'

### show storage classes for a given bucket
#for i in s3r.Bucket(BUCKET).objects.all():
#  print(i.key, i.storage_class)

### show buckets
#s3c.list_buckets()['Buckets']

for i in s3r.Bucket(BUCKET).objects.all():
  print(i.key, i.storage_class)

### example move to deep archive
#copy_source = {
#    'Bucket': BUCKET,
#    'Key': KEY
#}
#
#s3c.copy(
#  copy_source, BUCKET, KEY,
#    ExtraArgs = {
#    'StorageClass': 'DEEP_ARCHIVE',
#    'MetadataDirective': 'COPY'
#  }
#)
