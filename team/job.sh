#!/usr/bin/env bash
# job.sh <name> <cmd...>: run a solver under a 5G memory cap, log to runs/<name>.log, then merge all inputs.
cd "$(dirname "$0")"; name=$1; shift
systemd-run --user --scope -q -p MemoryMax=5G -p MemorySwapMax=0 "$@" > runs/$name.log 2>&1
echo "EXIT $? $name" >> runs/$name.log
for f in in/in_level-3_[1-4]*.txt; do .venv/bin/python merge.py $f; done >> runs/promote.log 2>&1
