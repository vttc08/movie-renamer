#!/bin/bash
# script for olivetin that calls another python script
source .env
cd $WORKING_DIR
# Activate the virtual environment
source ./venv/bin/activate

# Call the Python script with the user-defined argument
sudo -u karis ./venv/bin/python main.py "$1"

# Deactivate the virtual environment
deactivate
