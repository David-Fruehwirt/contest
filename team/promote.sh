#!/usr/bin/env bash
# promote.sh <in> <candidate_out> -- copy candidate to best/ only if valid and strictly cheaper.
set -u
cd "$(dirname "$0")"
in="$1"; cand="$2"
name=$(basename "$in"); name="out_${name#in_}"
best="best/$name"
new=$(python3 score.py "$in" "$cand" | awk '/^TOTAL/{print $2} /^INVALID/{print "INVALID"}')
if [ "$new" = "INVALID" ] || [ -z "$new" ]; then
  echo "REJECT $name: $(python3 score.py "$in" "$cand" | tail -1)"; exit 1
fi
if [ -f "$best" ]; then
  old=$(python3 score.py "$in" "$best" | awk '/^TOTAL/{print $2}')
  if [ "$new" -ge "$old" ]; then echo "KEEP $name: best=$old candidate=$new"; exit 2; fi
else old="none"; fi
chmod u+w "$best" 2>/dev/null; cp "$cand" "$best"; chmod 444 "$best"
echo "PROMOTE $name: $old -> $new"
