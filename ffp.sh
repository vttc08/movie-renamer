#!/bin/bash

# FFProbe Command
ffp='ffprobe *.mkv 2>&1>/dev/null | grep -E "Stream|title" | less'

eval $ffp # need to press q to quit

ffmbase='ffmpeg -i *.mkv'

submap() {
    read -p "Enter the index of the $1 stream (Ctrl-C to quit, enter if None): " index
    if [[ $index =~ ^[0-9]+$ ]]; then # if index is a number
        ffo="-map 0:$index $1"
    fi
    echo $ffo
}

eno=$(submap 'en.srt')
zho=$(submap 'zh.srt')


if [[ -z $eno && -z $zho ]]; then
    exit 0
elif [[ $index == 'q' ]]; then
    exit 0
fi

fffull="$ffmbase $eno $zho"
echo "Running command $fffull, press Ctrl-C to quit."
sleep 1.5
eval $fffull