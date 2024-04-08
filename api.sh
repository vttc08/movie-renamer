#!/bin/bash

fullpath=$1
source /config/movie-rename-script/.env
# source .env # if run locally

# Create the JSON payload if file is in /mnt/data
data=$(jq -n --arg path '"'"$fullpath"'"' '{"actionName": "Rename Movies", "arguments": [{"name": "path", "value": $path}]}')

# If the file is not in /mnt/data (eg. it's on another drive), move it to /mnt/data/nzbget (temp dir for processing)
if [[ "$fullpath" != /mnt/data* ]]; then
    # Move the folder with progress into /mnt/data/nzbget
    # define variables
    touch -d "2 seconds ago" "$1"/* # update the modified time since these files are not modified by nzbget
    basename=$(basename "$1")
    set -e # exit script on rsync error
    [ -f .fuse_hidden* ] && echo ".fusehidden found,\
 script will be stopped" && sleep 3 && exit 1 # exit script on .fuse_hidden files in dir
    rsync -a --progress --remove-source-files "$1" "/mnt/data/nzbget/" || sleep 5
    # rsync error will be printed if an error occured
    rmdir "$1" # only remove folder if it's empty
    set +e
    # Olivetin processing of the files in nzbget folder, new JSON payload is created with the nzbget path
    nzbpath="/mnt/data/nzbget/$basename"
    # Create payload for nzbpath
    newdata=$(jq -n --arg newpath '"'"$nzbpath"'"' '{"actionName": "Rename Movies", "arguments": [{"name": "path", "value": $newpath}]}')
    curl -X POST "$OLIVETIN_URL/api/StartAction" -d "$newdata"
else
    curl -X POST "$OLIVETIN_URL/api/StartAction" -d "$data"
fi