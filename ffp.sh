#!/bin/bash

# FFProbe Command
# Shortcut: Ctrl-Shift-A
# The script will try to automatically detect the subtitle streams in the mkv file with options for manual override.

help=$(cat <<EOF  
  q: quit, or Ctrl-C
  m: manually enter stream index for en and zh subtitles
  r: recheck the streams and index using old command for manual use
  rr: recheck the streams and index using the new json format
  h: help
  p: preview ffmpeg command
  *: confirm and run ffmpeg command
EOF
)

ffo="" # null, use side effects
ffcommand="ffmpeg -i *.mkv"

new_command="ffprobe -v quiet -print_format json -show_streams *.mkv"
output=$($new_command | jq -r '[.streams[]
      | select(.codec_type == "subtitle")
      | {index, language: (.tags.language // null), title: (.tags.title // null)}]') # get subtitle streams and format to simplified json array

check_json() {
    ### $1 is the json content to be piped to jq
    ### $2 is the language to check, eng or chi
    ### check_json "$output" 'eng' -> stream index or ''
    length=$(echo "$1" | jq  --arg LANG "$2" '[.[]|select(.language == $LANG) ] | length')
    case $length in
        '') stream="''";; # no stream found
        1) stream=$(echo "$1" | jq -r --arg LANG "$2" '[.[]|select(.language == $LANG)] | .[].index');; # one stream found
        *) stream=$(additional_check $2);; # multiple streams found, pick the first one
    esac
    echo $stream
}

additional_check() {
    ### $1 is the language to check, eng or chi
    ### additional_check 'eng' -> stream index or ''
    case $1 in
        eng) stream=$(echo "$output" | jq -r '[.[]|select(.language == "eng" and (.title // null | test("forced|sdh";"i") | not))] | .[0].index');; # pick the first non-forced, non-sdh stream
        chi) stream=$(echo "$output" | jq -r '[.[]|select(.language == "chi" and  (.title // null | test("traditional";"i") | not))] | .[0].index');; # pick the first zh stream
        *) stream="";;
    esac
    echo $stream
}

submapbuilder() {
    ### $1 is the stream index, $2 is the output file name
    ### submapbuilder 3 'en.srt' -> -map 0:3 'en.srt'
    index=$1
    if [[ $index =~ ^[0-9]+$ ]]; then # if index is a number
        ffo="$ffo -map 0:$index $2"
    fi
    echo $ffo
}

# get the detected streams
enstream=$(check_json "$output" 'eng')
zhstream=$(check_json "$output" 'chi')

# build the ffo options
ffo=$(submapbuilder $enstream 'en.srt')
ffo=$(submapbuilder $zhstream 'zh.srt')

# format the output for display
echo "$output" | jq --argjson en "${enstream:-null}" \
                    --argjson zh "${zhstream:-null}" \
    '. |= [{},{},{SELECTED_EN:$en, SELECTED_ZH:$zh},{},{}] + .' \
| jq -cC '.[]'  | less -R

manual_ffmpeg() {
    ### Manual FFmpeg Command, user inputs the stream index
    ffo="" # reset
    read -p "Enter the index of the en subtitle stream (Ctrl-C to quit, enter if None): " enindex
    enffo=$(submapbuilder $enindex 'en.srt')
    read -p "Enter the index of the zh subtitle stream (Ctrl-C to quit, enter if None): " zhindex
    zhffo=$(submapbuilder $zhindex 'zh.srt')
    ffo="$enffo $zhffo"
    run_ffmpeg
}

run_ffmpeg() {
    ### Run the ffmpeg command with the built ffo options
    if [[ -z $ffo ]]; then
        echo "ffmpeg options is empty, exiting."
        exit 0
    fi
    ffcommand="ffmpeg -i *.mkv $ffo"
    echo "Running command $ffcommand, press Ctrl-C to quit."
    sleep 1.5
    $ffcommand
    exit 0
}

while true
do
    echo -e "\033[0;34m"
    echo "${help}"
    echo -e "\033[0m"
    read -p "Select a CLI option: " option
    case $option in
        q) exit 0;;
        m) manual_ffmpeg;; # manual ffmpeg override
        r) ffprobe *.mkv 2>&1>/dev/null | grep -E "Stream|title" | less;; # re-run the old command for manual use
        rr) echo "$output" | jq --argjson en "${enstream:-null}" \
                    --argjson zh "${zhstream:-null}" \
    '. |= [{},{},{SELECTED_EN:$en, SELECTED_ZH:$zh},{},{}] + .' \
| jq -cC '.[]'  | less -R;; # re-run the json format output
        h) echo "${help}";;
        p) echo "Preview command: $ffcommand $ffo";;
        *) run_ffmpeg;;
    esac
done