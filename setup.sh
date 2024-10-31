#!/bin/bash

# Check if ENV_DIR is provided as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/virtualenv"
    exit 1
fi

# Set the virtual environment directory from the first argument
ENV_DIR="$1"

# Install Chrome and Python dependencies
sudo apt update
sudo apt install -y wget gnupg python3 python3-venv

# Add Google's signing key and repository
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -

sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
>> /etc/apt/sources.list.d/google-chrome.list'

# Install Google Chrome
sudo apt update
sudo apt install -y google-chrome-stable

# Create the virtual environment if it doesn't exist
if [ ! -d "$ENV_DIR/venv" ]; then
    python3 -m venv "$ENV_DIR/venv"
fi

# Activate the virtual environment
source "$ENV_DIR/venv/bin/activate"

# Upgrade pip and install dependencies
pip3 install --upgrade pip
pip3 install -r requirements.txt
