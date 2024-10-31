#!/bin/bash

find "$1" -iname "*.drc" -delete # drc is a marker file which could be created at a previous step
fullpath=$1
source /config/movie-rename-script/.env
# source .env # if run locally

# Create the JSON payload if file is in /mnt/data
data=$(jq -n --arg path '"'"$fullpath"'"' '{"actionId": "Rename Movies", "arguments": [{"name": "location", "value": $path}]}')

# If the file is not in /mnt/data (eg. it's on another drive), move it to /mnt/data/nzbget (temp dir for processing)
if [[ "$fullpath" != /mnt/data* ]]; then
    # Move the folder with progress into /mnt/data/nzbget
    loc=$(printf "data\ndata2" | fzf --header "Choose a directory in /mnt: ") # fzf selectbox, require /usr/bin/fzf to be installed `sudo apt install fzf -y`
    [[ ! -z $loc ]] || loc="data" # if destination is not set, defaults to /mnt/data
    touch -d "2 seconds ago" "$1"/* # update the modified time since these files are not modified by nzbget
    basename=$(basename "$1") # define variables
    set -e # exit script on rsync error
    [ -f .fuse_hidden* ] && echo ".fusehidden found,\
 script will be stopped" && sleep 3 && exit 1 # exit script on .fuse_hidden files in dir
    sleep 1 # add sleep timer so user can change to another folder before rsync deletes it
    rsync -a --progress --remove-source-files "$1" "/mnt/$loc/nzbget/" || sleep 5
    # rsync error will be printed if an error occured
    rmdir "$1" # only remove folder if it's empty
    set +e # script won't fail with error
    # Olivetin processing of the files in nzbget folder, new JSON payload is created with the nzbget path
    nzbpath="/mnt/$loc/nzbget/$basename"
    # Create payload for nzbpath
    newdata=$(jq -n --arg newpath '"'"$nzbpath"'"' '{"actionId": "Rename Movies", "arguments": [{"name": "location", "value": $newpath}]}')
    curl -X POST "$OLIVETIN_URL/api/StartAction" -d "$newdata"
else
    curl -X POST "$OLIVETIN_URL/api/StartAction" -d "$data"
fi
