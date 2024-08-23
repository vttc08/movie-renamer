#!/bin/bash

# FFProbe Command
ffprobe *.mkv 2>&1>/dev/null | grep -E "Stream|title" | less

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

fffull="ffmpeg -i *.mkv $eno $zho"
echo "Running command $fffull, press Ctrl-C to quit."
sleep 1.5
eval "ffmpeg -i *.mkv $eno $zho"