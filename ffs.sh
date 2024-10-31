#!/bin/bash

# File Level Command

# choose a reference only one can be chosen
reference=$(find "$1" \( -name "*.srt" ! -name "*bad.srt" -o -name "*.mkv" \) -print0 | xargs -0 -I {} basename "{}" | sort -t. -k2,2r -k1,1  | fzf --header="Pick a reference file, only one reference file can be choosen:")

escdir=$(printf '%q' "$1") # escape folder name if applicable

for i in "${@:2}"; do
  esci=$(printf '%q' "$i") # escape each file input
  i=$(basename "$esci") # simplify to basename
  if [[ "$i" == *bad.srt ]]; then new="${i/bad/}";elif [[ "$i" == *.mkv ]];then continue;else read -p "New filename for $i: " new; fi # skip mkv file, change *bad.srt to without the bad, else prompt for name
  [[ ! -z $new ]] || new=$i # if name is not given, assume basename
  [[ "$new" == *.srt ]] || new="$new".srt  # auto add .srt so user can input name only
  ssh mediaserver "cd $escdir; ffs '$reference' -i '$i' -o '$new'" # ssh command
done
echo ""
