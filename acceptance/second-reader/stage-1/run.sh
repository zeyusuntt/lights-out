#!/bin/sh
set -eu
if [ "$#" -ne 1 ]; then
  echo 'usage: run.sh <stage-folder>' >&2
  exit 2
fi
exec python3 "$(dirname "$0")/run.py" "$1"
