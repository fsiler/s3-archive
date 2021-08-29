#!/usr/bin/env python3
from boto3 import resource, client
s3c = client('s3')    # low level
s3r = resource('s3')  # high level

BUCKET                = 'fms-python-glacier-test'
KEY                   = 'MakeMKV_log.txt'
DESIRED_STORAGE_CLASS = 'DEEP_ARCHIVE'

### show storage classes for a given bucket
#for i in s3r.Bucket(BUCKET).objects.all():
#  print(i.key, i.storage_class)

### show buckets
#s3c.list_buckets()['Buckets']

### doesn't work
#for i in s3r.Bucket(BUCKET).objects.filter("Contents[?StorageClass=='STANDARD']"):
#  print(i.storage_class, i.size, i.key)

### lists folders in particular folder/Prefix
#for f in s3c.list_objects(Bucket=BUCKET, Prefix='html/', Delimiter='/')['CommonPrefixes']:
#  print(f)

### not possible (yet)
#for key in s3c.list_objects(Bucket=BUCKET, query='Contents[?StorageClass!=`DEEP_ARCHIVE`]'):
#  print(key)

### can't do this- only prefix
#for o in s3r.Bucket(name=BUCKET).objects.filter(Suffix="/"):
#   print(BUCKET, o.key)


### archive objects >200kB: works
#q = []
#t = 0
#for i in s3r.Bucket(BUCKET).objects.all():
##  print(dir(i))
#  print(i.storage_class, i.size, i.key)
#  if i.size > 200 * 1024 and i.storage_class != DESIRED_STORAGE_CLASS:
#    print("***** archiving file: ", i.key, i.size)
#    s3c.copy({'Bucket': BUCKET, 'Key': i.key},
#      BUCKET, i.key,
#      ExtraArgs = {
#        'StorageClass': DESIRED_STORAGE_CLASS,
#        'MetadataDirective': 'COPY' })
#  else:
#    q.append(i.key)
#    t += i.size
#
#print(q)
#print(t)

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
