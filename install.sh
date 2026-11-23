#!/bin/sh
# Safe wrapper: dry-run unless you pass --apply yourself.
exec python3 "$(dirname "$0")/install.py" "$@"
