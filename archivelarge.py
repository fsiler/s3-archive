#!/usr/bin/env python3
from csv                 import DictReader
from gzip                import open as gzopen
from sys                 import argv, stderr
from shlex               import quote as shquote
from urllib.parse        import unquote

DESIRED_STORAGE_CLASS = 'DEEP_ARCHIVE'
THRESHOLD = 128 * 1024

# courtesy https://stackoverflow.com/a/1094933
def sizeof_fmt(num, suffix="B"):
  for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
    if abs(num) < 1024.0:
      return f"{num:3.1f}{unit}{suffix}"
    num /= 1024.0
  return f"{num:.1f}Yi{suffix}"


if __name__ == '__main__':
  with gzopen(argv[1],'rt') as f:
    reader = DictReader(f)
    for o in reader:
      bucket = unquote(o['bucket'])
      key  = unquote(o['key'])
      size = int(o['size'])

      if size >= THRESHOLD and o['storageclass'] != DESIRED_STORAGE_CLASS:
        # XXX: may be some significant quoting issues with this
        print(f"aws s3 cp 's3://{bucket}/{key}' 's3://{bucket}/{key}' --storage-class {DESIRED_STORAGE_CLASS} --metadata-directive COPY;: {sizeof_fmt(size)}")
