#!/usr/bin/env bash
DEVMODE=false

# Installation Check: Verify that the SuperSploit directory exists in the user's home folder.
if [ ! -d "$HOME/.SuperSploit" ]; then
    if [ ! $DEVMODE ]; then
      echo "Error: Directory $HOME/.SuperSploit does not exist" >&2
      exit 1
    else
      # run the program from the source directory this
      echo "Running from source directory. This is not the intended way to run the program. development mode  is on"
      python3 "source/main.py"
      exit
    fi
fi

# Launch: Execute the main application logic using the Python 3 interpreter.
# The script is located within the hidden .SuperSploit directory in the user's home.
python3 "$HOME/.SuperSploit/source/main.py"
