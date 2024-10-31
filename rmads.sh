#!/bin/bash

# File Level Command

escdir=$(printf '%q' "$1")
echo "$escdir"
for i in "${@:2}"; do
  esci=$(printf '%q' "$i")
  ssh mediaserver "cd $escdir;bin=~/projects/movie-renamer/venv/bin/python;file=~/projects/movie-renamer/convertsub.py;\$bin \$file  $esci --remove-ads " # same as zht2s.sh but with additional argument
done
echo ""
echo "Terminal will close in 1s CTRL-C to close now."
sleep 1