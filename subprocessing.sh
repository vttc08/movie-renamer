#!/bin/bash

# File Level Command
# subprocessing.py
# Shortcut: Ctrl-Shift-D

escdir=$(printf '%q' "$1") # escape directory
for i in "${@:2}"; do
  esci=$(printf '%q' "$i") # escape file input
  ssh mediaserver "cd $escdir;bin=~/projects/movie-renamer/venv/bin/python;file=~/projects/movie-renamer/subprocessing.py;\$bin \$file  $esci " # ssh command, cd into directory, execute with venv python 
done
echo ""
echo "Terminal will close in 1s CTRL-C to close now."
sleep 1