"""
Single Python file that checks the queue folder for MKVToolNix jobs, execute them, cleanup.
Rename MKV and subtitle files with main.py and also handle Radarr move after MKVToolNix. Everything is done sequentially.
This script is meant to be run automated in systemd timer at midnight.

.queue file structure
L1 Shell command to execute the MKVToolNix merge
L2 Directory of the movie files (for main.py)
L3 MKV file path (for deletion after merge)
L4 Destination slug for Radarr data/data2 (for main.py)
"""

import os
import glob
import subprocess
import base64
from pathlib import Path
import yaml
import time
from radarr_move import move_movie

SCRIPTS_FOLDER = "/srv/scripts/radarr"
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

def process_mkvmerge(file_path: str) -> None:
    with open(file_path, "r") as f:
        content = f.read().splitlines()

    content = [line for line in content if line.strip() != ""]  # Remove empty lines
    shell_command, dir, mkvfile, dest_slug = content

    print(f"Executing command: {shell_command}")

    try:
        subprocess.run(f"{shell_command}", shell=True, timeout=1200) # do not check since the error code might be 1 for success
        clean_path = Path(dir)
        subprocess.run(["sudo", "chown", "-R", "1000:1001", str(clean_path)], check=True) # MKVToolNix Docker shell don't follow UID GID
        if len(glob.glob(str(clean_path)+"/"+"*.mkv")) > 1:
            os.remove(mkvfile) # cleanup MKV file after merge
            os.remove(file_path) # cleanup .queue task
        else:
            raise Exception("MKVMerge never occured!")
        # run python script directly
        b64_dir = base64.b64encode(dir.encode('utf-8')).decode('utf-8')
        subprocess.run(f"{CURRENT_PATH}/venv/bin/python {CURRENT_PATH}/main.py {b64_dir} {dest_slug}", shell=True, check=True)
        # this process will create new .yaml file in the output folder for the Radarr move operation
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
    except subprocess.TimeoutExpired:
        print("Command timed out.")

if __name__ == "__main__":
    # Process MKVToolNix merge tasks
    queue_files = [f for f in os.listdir(SCRIPTS_FOLDER) if f.endswith('.queue')]
    for file in queue_files:
        file_path = os.path.join(SCRIPTS_FOLDER, file)
        process_mkvmerge(file_path)
    # Process Radarr move tasks
    yaml_files = [f for f in os.listdir(SCRIPTS_FOLDER) if f.endswith('.yaml')]
    for file in yaml_files:
        file_path = os.path.join(SCRIPTS_FOLDER, file)
        with open(file_path, 'r') as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)
            print(f"Moving movie to {yaml_data['path']} with ID {yaml_data['id']}")
            move_movie(yaml_data)
        os.remove(file_path) # cleanup .yaml task after processing
    time.sleep(10) # allow another systemd service to run its tasks before stopping