#!/usr/bin/env python3
from boto3               import client
from botocore.exceptions import ClientError
from csv                 import DictReader
from sys                 import argv, stderr
from urllib.parse        import unquote

s3c = client("s3")
DESIRED_STORAGE_CLASS = 'DEEP_ARCHIVE'
THRESHOLD = 128 * 1024

def changestorageclass(bucket, key, desired_class=DESIRED_STORAGE_CLASS):
  try:
    s3c.copy({'Bucket': bucket, 'Key': key},
             bucket, key,
             ExtraArgs = {
               'StorageClass': desired_class,
               'MetadataDirective': 'COPY' })
  except ClientError as e:
    if e.response['Error']['Code'] == 'InvalidObjectState':
      print(f"had issue changing storage class ({e})", file=stderr)
    else:
      print(f"got error {e}, continuing", file=stderr)

# courtesy https://stackoverflow.com/a/1094933
def sizeof_fmt(num, suffix="B"):
  for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
    if abs(num) < 1024.0:
      return f"{num:3.1f}{unit}{suffix}"
    num /= 1024.0
  return f"{num:.1f}Yi{suffix}"

if __name__ == '__main__':
  with open(argv[1]) as f:
    reader = DictReader(f)
    for o in reader:
      size = int(o['size'])
      key  = unquote(o['key'])
      if size >= THRESHOLD and o['storageclass'] != DESIRED_STORAGE_CLASS:
        print(f"archiving {key} ({sizeof_fmt(size)})", flush=True)
        changestorageclass(o['bucket'], key)