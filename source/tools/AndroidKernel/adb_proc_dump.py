import ppadb.client as adb

import subprocess
import sys

proc_files = []

def Start(args=None):
    print("Supersploit ADB tool...")
    print("Author: Donald ford")
    print("=" * 50)

    adbClient = adb.Client()
    devices = adbClient.devices()
    for x in devices:
        print(f"{devices.index(x)}: {x.serial}")

    print("=" * 50)
    device = devices[int(input("[*] Please enter the index of the device: "))]
    device_serial = device.serial
    input(f"[*] Proceeding with {device_serial} press enter to continue.")
    print("=" * 50)
    print(f"Readable content of proc folder")
    print("=" * 50)
    for x in device.shell("ls -al /proc/").split("\n"):
        if "-r--r--r-" in x:
            print(x)
            proc_files.append(x)
    e = []
    for y in proc_files:
        f = y.split(" ")[len(y.split(" "))- 1]
        e.append(f)

    print("=" * 50)
    print(f"Dumping proc files")
    print("=" * 50)
    for a in e:
        print("=" * 50)
        print(f"dumping proc/{a}")

        try:
            print(device.shell(f"cat /proc/{a}"))
        except UnicodeError:
            pass
        print("=" * 50)

Start(None)