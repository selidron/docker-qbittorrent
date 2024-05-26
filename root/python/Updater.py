#!/usr/bin/python3

import subprocess

class Updater:
    def __init__(self) -> None:
        # Use git to check for changes
        git = subprocess.Popen(['git', '-C', '/python'])
