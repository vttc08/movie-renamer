#!/bin/bash
fullpath=/mnt$1
source /config/movie-rename-script/.env


if [[ "$fullpath" != /mnt/data* ]]; then
    # Move the folder with progress into /mnt/data/nzbget
    basename=$(basename "$1")
    touch progress.txt
    rsync -a --progress "$1" "/data/nzbget/" & 
    pid=$!
    trap "kill $pid 2> /dev/null" EXIT
    s=0
    # While copy is running...
    start=$(date +%s)
    while kill -0 $pid 2> /dev/null; do
        basename=$(basename "$1")
        source_size=$(du -ks "$1" | awk '{print $1}')
        target_size=$(du -s "/data/nzbget/$basename" | awk '{print $1}')
        progress=$(printf "%.1f%%" $(echo "scale=3; $target_size/$source_size*100" | bc 2>/dev/null))
        seconds=$(($(date +%s) - $start))
        rate=$(printf "%.2f MBps" $(echo "scale=3; $target_size/$seconds/1024" | bc 2>/dev/null))
        mv progress* "progress $progress-$rate.txt"
        sleep 1
    done


    rm progress*.txt
    rm -rf "$1"
    # Disable the trap on a normal exit.
    trap - EXIT
    new_path="/mnt/data/nzbget/$basename"
    curl -X POST ''$OLIVETIN_URL'/api/StartAction' -d '{"actionName": "Rename Movies", "arguments": [{"name": "path", "value": "'"'$new_path'"'"}]}'
else
    curl -X POST ''$OLIVETIN_URL'/api/StartAction' -d '{"actionName": "Rename Movies", "arguments": [{"name": "path", "value": "'"'$fullpath'"'"}]}'
fi