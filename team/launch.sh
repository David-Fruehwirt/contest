#!/usr/bin/env bash
# launch.sh <name> <script.py> <args...>: start a capped background job (see job.sh)
cd "$(dirname "$0")"; n=$1; shift
nohup ./job.sh "$n" .venv/bin/python "$@" >/dev/null 2>&1 &
echo "started $n"
