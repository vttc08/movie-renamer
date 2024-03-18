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
    rsync -a --progress --exclude 'progress*.txt' "$1" "/mnt/data/nzbget/" 
    rm -rf "$1" # dangerous
    # Olivetin processing of the files in nzbget folder, new JSON payload is created with the nzbget path
    newpath="/mnt/data/nzbget/$basename"
    newdata=$(jq -n --arg path '"'"$newpath"'"' '{"actionName": "Rename Movies", "arguments": [{"name": "path", "value": $path}]}')
    curl -X POST "$OLIVETIN_URL/api/StartAction" -d "$newdata"
else
    curl -X POST "$OLIVETIN_URL/api/StartAction" -d "$data"
fi