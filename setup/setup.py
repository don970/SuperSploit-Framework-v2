#!/bin/python3
import json
from os import getenv
from subprocess import run
import pathlib

try:
    import prompt_toolkit
except ImportError:
    prompt_cmd = "sudo apt-get install python3-prompt-toolkit"
    run(prompt_cmd.split())

from prompt_toolkit import prompt as input

# first lets set up important variables
home = getenv("HOME")
installation = pathlib.Path(f'{home}/.SuperSploit')

# now create a class called SuperSploit
class SuperSploit:

    def __init__(self):
        self.setup_directories()
        self.create_aliases()
        self.install_dependencies()

    def setup_directories(self):
        """Ensure all required hidden data and loot directories exist."""
        subdirs = [
            ".data/.config",
            ".data/.history",
            ".data/.logs",
            ".data/.errors",
            ".data/.loot/reports",
            ".data/.cache",
            ".data/.targets",
            "exploits",
            "recon",
            "payloads"
        ]
        for subdir in subdirs: 
            path = installation / subdir
            path.mkdir(parents=True, exist_ok=True)

    def create_aliases(self):
        """Create the framework alias mapping and persist to JSON."""
        a = {
            "ss": str(installation),
            "~": home,
            "config": str(installation / ".data/.config"),
            "db": str(installation / ".data/.config/data.db"),
            "history": str(installation / ".data/.history/history"),
            "install_dir": str(installation),
            "logs": str(installation / ".data/.logs"),
            "nmapDb": str(installation / ".data/.config/nmap-os-db.txt"),
            "aliases": str(installation / ".data/.config/Aliases.json"),
            "exploits": str(installation / "exploits"),
            "recon": str(installation / "recon"),
            "assets": str(installation / ".data/.config/.assets/"),
            "activity": str(installation / ".data/.logs/activity.log"),
            "targets": str(installation / ".data/.config/targets.json"),
            "reports": str(installation / ".data/.loot/reports"),
            "templates": str(installation / "templates"),
            "payloads": str(installation / "payloads")
        }
        
        alias_file =  f"{installation}/.data/.config/Aliases.json"
        with open(alias_file, "w") as file:
            json.dump(a, file, sort_keys=True, indent=4)

    def install_dependencies(self):
        """Install required Python libraries from requirements.txt."""
        req_path = installation / "setup" / "requirements.txt"
        if req_path.exists():
            run(["pip3", "install", "-r", str(req_path), "--break-system-packages"])


SuperSploit()
