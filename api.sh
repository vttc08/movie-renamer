#!/bin/bash

fullpath=/mnt$1
source /config/movie-rename-script/.env
# source .env # if run locally

# If the file is not in /mnt/data, move it to /mnt/data/nzbget (temp dir for processing)
# the script is execute in the POV of webtop where /data is /mnt/data on the host and /data/nzbget is /mnt/data/nzbget on the host
if [[ "$fullpath" != /mnt/data* ]]; then
    # Move the folder with progress into /mnt/data/nzbget
    # define variables
    touch -d "2 seconds ago" "$1"/* # set the modified time of the file to 2 seconds ago
    basename=$(basename "$1")
    start=$(date +%s)
    touch progress.txt # progress.txt is used in thunar to display progress
    # rsync copy with progress
    rsync -a --progress --exclude 'progress*.txt' "$1" "/data/nzbget/" & 
    pid=$! # declare pid of rsync
    trap "kill $pid 2> /dev/null" EXIT
    # While copy is running...
    while kill -0 $pid 2> /dev/null; do
        basename=$(basename "$1")
        source_size=$(du -ks "$1" | awk '{print $1}')
        target_size=$(du -s "/data/nzbget/$basename" | awk '{print $1}')
        progress=$(printf "%.1f%%" $(echo "scale=3; $target_size/$source_size*100" | bc 2>/dev/null))
        seconds=$(($(date +%s) - $start))
        rate=$(printf "%.2f MBps" $(echo "scale=3; $target_size/$seconds/1024" | bc 2>/dev/null))
        mv progress* "progress $progress-$rate.txt" # create an ever updating text file with progress
        sleep 1
    done
    # remove residual files
    rm progress*.txt
    rm -rf "$1"
    # Disable the trap on a normal exit.
    trap - EXIT
    # Olivetin processing of the files in nzbget folder
    new_path="/mnt/data/nzbget/$basename"
    curl -X POST ''$OLIVETIN_URL'/api/StartAction' -d '{"actionName": "Rename Movies", "arguments": [{"name": "path", "value": "'"'$new_path'"'"}]}'
else
    curl -X POST ''$OLIVETIN_URL'/api/StartAction' -d '{"actionName": "Rename Movies", "arguments": [{"name": "path", "value": "'"'$fullpath'"'"}]}'
fi