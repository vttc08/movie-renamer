#!/usr/bin/env bash
# ---------------------------------------------------------------
# MKVMerge folder-level auto-muxer
#   - Detects main MKV and external subs (en, zh, mul)
#   - Auto-selects or interactively picks audio/sub tracks
#   - Builds a safe mkvmerge command and runs inside Docker
#   - Shortcut: Ctrl-Shift-E
# ---------------------------------------------------------------

set -euo pipefail

# --- CONFIG -----------------------------------------------------
mkvtoolnix_container="mkvtoolnix"
mkvmergebin=(docker exec -i "$mkvtoolnix_container" /usr/bin/mkvmerge)
declare -A subtitle_mappings=(["en"]="英文字幕" ["zh"]="中文字幕" ["mul"]="中英文字幕")
declare -A lang_idx_map=(["eng"]="en" ["chi"]="zh" ["mul"]="mul")
DRY_RUN=${DRY_RUN:-0}        # export DRY_RUN=1 for preview mode
SLEEP=${SLEEP:-60}           # seconds to wait before deleting source files
# ----------------------------------------------------------------

this_script_dir=$(dirname ${BASH_SOURCE[0]})
source $this_script_dir/.env
dir="${1:?Usage: $0 <directory>}"
dir="${dir%/}"

# --- Helpers ----------------------------------------------------
run_jq() { jq -r "$1" <<<"$mkvinfo"; }

get_track_property() { run_jq "[.tracks[]|select(.id==$1)][0].$2"; }

join_by() { local IFS="$1"; shift; echo "$*"; }

quote() { printf '%q' "$1"; }
subtitle_file_idx=1

render_subtitle() {
  local file="${1:-}" lang base
  [[ -z $file ]] && { echo "render_subtitle: no input file" >&2; return 1; }

  base="$(basename "$file")"
  lang="${base%.*}"

  [[ -z "${subtitle_mappings[$lang]:-}" ]] && return
  subtitle_cmd+=(--language 0:"$lang" --track-name 0:"${subtitle_mappings[$lang]}" "(" "$file" ")")
  track_order_extra+=",${subtitle_file_idx}:0"
  ((subtitle_file_idx++))
}

# --- Detect base MKV --------------------------------------------
mkvfile=$(find "$dir" -maxdepth 1 -type f -iname "*.mkv" | head -n1)
[[ -z $mkvfile ]] && { echo "No MKV found in $dir"; exit 1; }

mkvinfo="$("${mkvmergebin[@]}" -J "$mkvfile")"
mkvfilename="${mkvfile##*/}"
mkvfilename="${mkvfilename%.*}"
mkvout="$dir/$mkvfilename.MUX.mkv"

# --- Detect internal tracks -------------------------------------
audio_ids=($(run_jq '[.tracks[]|select(.type=="audio")]|.[].id'))
subtitle_ids=($(run_jq '[.tracks[]|select(.type=="subtitles" and (.codec|test("HDMV")|not))]|.[].id'))

detect_tracks() {
  local lang="$1"
  run_jq "[.tracks[]|select(.type==\"subtitles\" and ((.properties.language_ietf==\"$lang\") or (.properties.language==\"${lang_idx_map[$lang]:-$lang}\")) and (.codec|test(\"HDMV\")|not))]|length"
}

en_count=$(detect_tracks "en")
zh_count=$(detect_tracks "zh")

# --- External subtitle attachments ------------------------------
subtitle_cmd=()
track_order_extra=""

for lang in en mul zh; do
  subfile="$dir/$lang.srt"
  [[ -f $subfile ]] && render_subtitle "$subfile"
done

# --- Audio/subtitle selection -----------------------------------
if (( en_count>1 || zh_count>1 || ${#audio_ids[@]}>1 )); then
  echo "Multiple audio/subtitle tracks found — interactive mode"
  audio_track_idx=$(run_jq '[.tracks[]|select(.type=="audio")] |
    .[] | (.properties.language_ietf // .properties.language) + " :: " +
    .properties.track_name + " :: " + .codec + " :: " + (.id|tostring)' |
    fzf --multi --header "Select audio tracks" \
        --bind 'ctrl-a:select-all,ctrl-d:deselect-all' \
    | awk -F' :: ' '{print $4}')
    [[ -z $audio_track_idx ]] && exit 1
    set +e
    subtitle_track_idx=$(run_jq '[.tracks[]|select(.type=="subtitles" and (.codec|test("HDMV")|not))] |
    .[] | (.properties.language_ietf // .properties.language) + " :: " +
    .properties.track_name + " :: " + .codec + " :: " + (.id|tostring)' |
    fzf --multi --header "Select subtitle tracks" \
        --bind 'ctrl-a:select-all,ctrl-d:deselect-all' \
    | awk -F' :: ' '{print $4}')
    set -e
else
  audio_track_idx="${audio_ids[*]}"
  en_ids=($(run_jq '[.tracks[]|select(.type=="subtitles" and ((.properties.language_ietf=="en") or (.properties.language=="eng")) and (.codec|test("HDMV")|not))]|.[].id'))
  zh_ids=($(run_jq '[.tracks[]|select(.type=="subtitles" and ((.properties.language_ietf=="zh") or (.properties.language=="chi")) and (.codec|test("HDMV")|not))]|.[].id'))
  subtitle_track_idx="${en_ids[*]}${en_ids[*]:+ }${zh_ids[*]}"
fi

# --- Build command pieces ---------------------------------------
ats=(--audio-tracks "$(join_by , $audio_track_idx)")
sts=()
printf 'subtitle_track_idx=<%q>\n' "$subtitle_track_idx"
[[ -n ${subtitle_track_idx} ]] && sts=(--subtitle-tracks "$(join_by , $subtitle_track_idx)")

track_order_pre=(--track-order "0:0")
audio_subtitle_opts=()

for idx in $audio_track_idx $subtitle_track_idx; do
  lang=$(get_track_property "$idx" "properties.language_ietf")
  [[ -z $lang || $lang == "null" ]] && lang=$(get_track_property "$idx" "properties.language")
  lang=${lang_idx_map[$lang]:-$lang}
  name=$(get_track_property "$idx" "properties.track_name")
  audio_subtitle_opts+=(--language "$idx:$lang" --track-name "$idx:$name")
  track_order_pre[1]+=",0:$idx"
done

[[ -z $subtitle_track_idx ]] && audio_subtitle_opts+=("--no-subtitles")

disp_dim=$(get_track_property 0 "properties.display_dimensions")
video_opts=(--language 0:und)
[[ -n $disp_dim && $disp_dim != "null" ]] && video_opts+=(--display-dimensions 0:"$disp_dim")
track_order="${track_order_pre[*]}${track_order_extra}"

# --- Compose final command --------------------------------------
cmd=("${mkvmergebin[@]}" -o "$mkvout" "${sts[@]}" "${ats[@]}" \
     "${video_opts[@]}" "${audio_subtitle_opts[@]}" "(" "$mkvfile" ")" \
     "${subtitle_cmd[@]}" $track_order)

echo "---------------------------------------------------------------"
echo "MKV Command:"
printf '%q ' "${cmd[@]}"
echo
echo "---------------------------------------------------------------"

# --- Move file settings -----------------------------------

# Snippet from api.sh
if [[ "$dir" != /mnt/data* ]]; then
    # Move the folder with progress into /mnt/data/nzbget
  loc=$(df -BG --output=target,avail /mnt/data* 2>/dev/null \
        | awk 'NR>1 && $1 ~ /^\/mnt\/data/ {
            split($1,p,"/");
            name=p[3];
            avail=$2;
            gsub(/G$/,"",avail);
            printf "%s\t%s - %.3f TB\n", name, name, avail/1000
        }' \
        | sort -u \
        | fzf --header "Choose a destination directory in /mnt: " \
        | awk -F '\t' '{ print $1 }')
    find "$dir" -mindepth 1 -maxdepth 1 -exec touch -d '2 seconds ago' -- {} + # update the modified time since these files are not modified by nzbget
else
    IFS='/' read -r -a dir_array <<< "$dir"
    loc=${dir_array[2]}
fi

# --- Execute -----------------------------------------------------
if (( DRY_RUN )); then
  echo "Dry-run mode: not executing."
  exit 0
fi

# Option to queue the command in a file for later execution or execute immediately
read -p "Click any key to queue the command, click y to execute immediately..." d
if [[ $d == "y" ]]; then
  "${cmd[@]}"
  echo "✅ Mux complete: $mkvout"
  trap "echo -e '\nProcess interrupted, nothing deleted.'; exit 1" SIGINT SIGTERM
  rm "$mkvfile"
  # python script callback
  $this_script_dir/venv/bin/python $this_script_dir/main.py "$dir" $loc
  sleep $SLEEP
else
  echo "Command queued for later execution:"
  queued_file="/srv/scripts/radarr/mkvmerge_queue_$(date +%s)"
  printf '%q ' "${cmd[@]}" > "$queued_file.queue" # line 1
  echo -e >> "$queued_file.queue" # separator
  echo $dir >> "$queued_file.queue"
  echo $mkvfile >> "$queued_file.queue"
  echo $loc >> "$queued_file.queue"
  # rm "$mkvfile" will need to be handled separately
fi


# Callback
