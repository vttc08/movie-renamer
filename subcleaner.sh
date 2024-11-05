#!/bin/bash

# File Level Command

# This command is meant to be run on host.

# Expect 2 inputs, 1st is the directory, 2nd is the file name.

dir="$1"
file="$2"
escf=$(printf '%q' "$file")
path="$dir/$file"
src=$(dirname ${BASH_SOURCE[0]})
pybin="$src/subcleaner/venv/bin/python"
pybin2="$src/venv/bin/python"
pytestbin="$src/subcleaner/venv/bin/pytest"
subcleaner="$src/subcleaner/subcleaner.py"
helper="$src/subcleaner/helper.py"
convertsub="$src/convertsub.py"
zhregex="$src/subcleaner/regex_profiles/default/chinese.conf"
help=$(cat <<EOF  
  q: quit
  Y: Continue to cleaning subtitle (default)
  r: Re-analyze subtitle
  a: add regex to blacklist
  t: test against regex blacklist
  x: except mode: remove all detected ads except the selected lines
  c: cut mode: remove these lines from the subtitle
  g: automatic update of regex to Github  
  u: use this subtitle as a test case for false positive (use only after cleaning)
  f: fix traditional to simplified and UTF-8 encoding
  h: help
EOF
)

$pybin $subcleaner "$file" "-n"

while true 
do
  curr_file=$(basename "$escf")
  echo -e "‘\033[0;34m"
  read -p "File: $curr_file; Choose an option [Y|q|r|a|t|(x|c ...)|g|u|f|h], h for help: " option
  echo -e "\033[0m"
  case $option in
    q) break;;
    h) echo "${help}";;
    r) $pybin $subcleaner "$file" "-n";;
    c*|x*) $pybin $helper "$file" $option;;
    a) nano +11,15 $zhregex;;
    t) cd $(dirname $subcleaner); $pytestbin -s --disable-warnings -q --tb=no testing.py; cd $src;;
    g) cd $(dirname $subcleaner); bash git.sh; cd $src;;
    f) $pybin2 $convertsub "$file";;
    u) read -p "Rename this .srt file as (foreign|zh).(movie|tv).<genre>.year.name: " rename; if [[ ! -z $rename ]]; then rename="$rename.srt"; else rename=$curr_file; fi ; cp "$file" "$(dirname $subcleaner)/sub_tests/good/$rename"; echo "$rename has been added as a test case.";;
    *) $pybin $subcleaner "$file";;
  esac
done

