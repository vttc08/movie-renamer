#!/bin/bash

# File Level Command

escdir=$(printf '%q' "$1")
ssh mediaserver -t "cd $escdir;bin=~/projects/movie-renamer/mkvmerge.sh;\$bin $escdir" 
