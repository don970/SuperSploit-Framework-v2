import json
import os
import traceback

from .database import DatabaseManagment
from .errors import Error
from .ToStdOut import ToStdout

installation = f'{os.getenv("HOME")}/.SuperSploit'


class SetV:
    @classmethod
    def SetV(cls, data):
        db = DatabaseManagment.get()
        try:
            args = data.split()
            if len(args) < 3: # Changed from < 2 to < 3 to ensure data[2] exists
                print("[-] No arguments supplied for set\n[-] Usage: set <VARIABLE> <VALUE>\n")
                return
                
            key = args[1]
            value = " ".join(args[2:])
            # Type casting for booleans
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False

            variables = db

            key_map = {
                "exploit": "EXPLOIT",
                "payload": "PAYLOAD",
                "target": "R_HOST",
                "port": "R_PORT",
                "verbose": "VERBOSE_LOGGING",
                "dev_mode": "DEV_MODE",
                "host": "L_HOST",
                "l_port": "L_PORT",
                "port_range": "PORT_RANGE",
                "generated_payload": "GENERATED_PAYLOAD",
                "comp_arch": "COMP_ARCH",
                "comp_static": "COMP_STATIC",
                "comp_out": "COMP_OUT",
                "app_name": "APP_NAME",
                "compiler": "COMPILER",
                "cc": "COMPILER"
            }

            mapped = False
            for k, internal_key in key_map.items():
                if k == key.lower():
                    key = internal_key
                    mapped = True
                    break

            # Auto-uppercase standardized variables if no alias is used
            if not mapped:
                key = key.upper()

            # Direct assignment handles both updating AND adding new variables
            variables[key] = value

            print(f"[*] {key} => {value}\n")
            

        except Exception:
            Error(traceback.format_exc())