#!/bin/bash

find "$1" -iname "*.drc" -delete # drc is a marker file which could be created at a previous step
# Merged rmass.sh functionality to remove unwanted subtitle files
find "$1" -name "*.ass" -delete
find "$1" -name "*bad.srt" -delete
fullpath=$1
b64=$(printf %s "$1" | base64 -w0) # encode the path to handle special characters and spaces
source /config/movie-rename-script/.env
# source .env # if run locally

escdir=$(printf '%q' "$1")
if [[ "$fullpath" != /mnt/data* ]]; then
    loc=$(printf "data\ndata2\ndata3" | fzf --header "Choose a directory in /mnt: ") # fzf selectbox, require /usr/bin/fzf to be installed `sudo apt install fzf -y`
    [[ ! -z $loc ]] || loc="data" # if destination is not set, defaults to /mnt/data
fi

ssh mediaserver  \
    "cd ~/projects/movie-renamer; ./venv/bin/python main.py "$b64" "$loc";"

