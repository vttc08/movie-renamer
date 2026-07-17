#!/bin/bash

# File Level Command
# The first selected subtitle is displayed above the second.

if [[ $# -ne 3 ]]; then
  echo "Usage: $0 DIRECTORY FIRST.srt SECOND.srt" >&2
  echo "Select exactly two SRT files, with English first if desired." >&2
  exit 2
fi

escdir=$(printf '%q' "$1")
first_subtitle=$(printf '%q' "$2")
second_subtitle=$(printf '%q' "$3")

ssh mediaserver \
  "cd $escdir || exit; bin=~/projects/movie-renamer/venv/bin/python; file=~/projects/movie-renamer/mergesub.py; \$bin \$file $first_subtitle $second_subtitle"
status=$?

echo ""
if [[ $status -eq 0 ]]; then
  echo "Created mul.srt. Terminal will close in 1s; CTRL-C to close now."
  sleep 1
fi
exit "$status"
