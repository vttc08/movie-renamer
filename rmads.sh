#!/bin/bash

# File Level Command

escdir=$(printf '%q' "$1")
for i in "${@:2}"; do
  esci=$(printf '%q' "$i")
  ssh mediaserver -t "cd $escdir;bin=~/projects/movie-renamer/subcleaner.sh;\$bin $escdir $esci" 
done
