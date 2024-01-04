# Movie Renamer

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Description

Rename simple subtitle files into user friendly names for Jellyfin. Also rename mkv files in folders with more than 1 mkv files into appropriate names for Jellyfin to recognize.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

Instructions on how to install and set up your project.

## Usage

### Install Dependencies

```shell
python3 -m venv your-venv # optional
```
activate the virtual environment
```shell
pip install -r requirement.txt
```

### Windows (Input Based)

Simply run start.bat and input the folder accordingly.

### Linux 



This is for use of this script with webtop and [OliveTin](https://github.com/OliveTin/OliveTin).

`start.sh` this is the script which OliveTin will call, since there are errors for Olivetin when calling python script directly with arguments, this script is used

`api.sh` script used in the webtop container, this script is called when right clicking on a folder in thunar 

`mover.sh` script is responsible for moving files to the appropriate directories for webtop to access 

```sh
chmod +x *.sh
```
make all the scripts executable

#### For Webtop/Thunar

Install dependencies
```sh
sudo apt install rsync -y
```
Use the mover script to move api.py and .env to the correct location.

In Thunar, go to Edit > Configure Custom Actions
```
/config/movie-rename-script/script.sh %f
```
This is the command of the thunar custom actions, where /config/movie ... is the location of script in webtop and %f means the directory name.


## License

This project is licensed under the [MIT License](LICENSE).
