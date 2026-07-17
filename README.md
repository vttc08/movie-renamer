# Project Name

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Description

Rename simple subtitle files into user friendly names for Jellyfin. Also rename mkv files in folders with more than 1 mkv files into appropriate names for Jellyfin to recognize. Include additional features such as subtitle extraction, UTF-8 and traditional Chinese fix, subtitle synchronization, format conversion, SDH removal and subtitle cleanup.

## Table of Contents

- [Usage](#usage)
- [License](#license)


## Usage

### Install Dependencies (Host Machine)

```shell
python3 -m venv your-venv # optional
```
activate the virtual environment
```shell
pip install -r requirement.txt
```
When running the python script, if a virtual environment is used, make sure to use the venv python.

### Windows (Input Based)

Simply run start.bat and input the folder accordingly.

### Linux 

This is for use in webtop, an isolated environment for media management in a docker containers. The isolated Docker container comes with challenges:

- applications and dependencies are not persistent on container recreation
- Python and its requirements `python3`, `pip` and other dependencies in a virtual environment are very large in size and can become bloated

To overcome these, [OliveTin](https://github.com/OliveTin/OliveTin) API and SSH commands are used. This offload processing that require python or large dependencies to the host machine where programs and configurations are persistent, and python is already installed. The webtop container will only need to call the API or SSH commands.

#### For Webtop/Openbox/SpaceFM

The dependencies are now tracked in another git repository, built as a [Linuxserver Docker Mods](https://github.com/vttc08/docker-mods-webtop). For Docker deployment of webtop, need to add this line to the docker-compose.yml file.
```yaml
      - DOCKER_MODS=vttc08/docker-mods-webtop:latest
```
Upon deployment, all dependencies will be installed. All configurations will be inherited from the `~/docker/webtop/config` directory so ensure these are backed up before redeployment.

Use the mover script to move all the `.sh` files to the correct location.

**The SpaceFM Custom Actions are as follows:**

`Ctrl-Shift-S` - `api.sh` - Calls the script that removed marker file, and sends the folder to OliveTin API which calls the python script to process the folder of subtitles; if the folder is not located on the HDD(s) containing the movie folders (eg. at a NVMe data or cache drive), the script will prompt user to select the destination and move the files to it via rsync with tracking progress.

`Ctrl-Shift-A` - `ffp.sh` - Calls the script that runs `ffprobe` and prompt user to enter track number to extract subtitles from `mkv` file if needed.

~~`Ctrl-Shift-D` - `rmass.sh` - Calls the cleanup script that remove bad subtitles and unused `.ass` files.~~ Deprecated, removing `.ass` files is now implemented in `api.sh` as final cleanup.

`Ctrl-Shift-D` - `subprocessing.sh` - Calls the script that process `.ass` files, convert into `.srt`, remove SDH lines and fix traditional Chinese to simplified Chinese and UTF-8 encoding. It's a one-shot script that does common subtitle operation with default options.

`Ctrl-Shift-M` - `mergesub.sh` - Select exactly two `.srt` files and preprocess the subtitle first by removing line breaks and merge 2 subtitle together so the first shows on the first line while the second show on second line to create multi-language subtitle `mul.srt`. To reduce flicker from slightly misaligned subtitle tracks, repeated-line transition fragments are removed when their whole contiguous run is shorter than 500 ms. Longer transition runs and standalone short subtitles are preserved. Both inputs must contain valid cues and are limited to 20 MiB each before parsing.

`Ctrl-Shift-Z` - `zht2s.sh` - Calls the script that send files and the directory as input over SSH which will process and overwrite the files with UTF-8 encoding and traditional Chinese to simplified Chinese conversion. OliveTin is not used because tracking the progress is needed.

`Ctrl-Shift-X` - `ffs.sh` - Calls the script that send files and the directory as input over SSH to [ffsubsync](https://github.com/smacke/ffsubsync) which will process and synchronize the subtitles against a reference file a user selected via `fzf`.

`Shift-Z` - `rmads.sh` - Calls the script that remove ads from subtitles, not implemented yet.

`Manual Right Click` - Manual action that create a marker file in `.drc` format with string `中英文字幕` as file name. This is used for MKVToolNix VNC container where it's difficult to copy and paste Chinese characters into it, it's difficult in the program to write Chinese on systems without Chinese input method. `.drc` is recognized by MKVToolNix so user can utilize the folder dialog box to copy Chinese characters. The marker file is removed by the `api.sh` script.

#### Updated Userscript

The updated workflow added functionality to automatically use Cloudflare Workers free tier AI model to run OCR and solve the image. The code is already developed on Cloudflare and is tracked in another repo in a submodule.

The current project consists of `userscript.template.js` which is used to generate `userscript.js`, to be used for [Tampermonkey](https://addons.mozilla.org/en-CA/firefox/addon/tampermonkey/).

## License

This project is licensed under the [MIT License](LICENSE).
