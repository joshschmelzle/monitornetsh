#!/usr/bin/env python3
#-*- coding: utf-8 -*-
"""
Gets signal quality from netsh.exe and converts it to rssi dbm.
"""
import sys
import subprocess

command = ['netsh', 'wlan', 'show', 'interface']
netsh_output = ""
quality = ""
dbm = 0
bssid = ""
channel = ""

try:
    netsh_output = subprocess.check_output(command)
except subprocess.CalledProcessError as ex:
    print("error getting netsh output")
    sys.exit(-1)

netsh_output = netsh_output.decode("utf-8").lower()
for i, line in enumerate(netsh_output.splitlines()):
    if "state" in line:
        state = line.split(":")[1].strip()
        if "disconnect" in state:
            print("not connected")
            sys.exit(0)
    if "bssid" in line:
        bssid = line.split(":", 1)[1].strip()
    if "channel" in line:
        channel = line.split(":", 1)[1].strip()
    if "signal" in line:
        quality = int(line.split(":", 1)[1].strip().replace("%", ""))

if quality <= 0:
    dbm = -100
elif quality >= 100:
    dbm = -50
else:
    dbm = (quality / 2) - 100
dbm = int(dbm)

print("bssid,channel,quality,dbm")
print("{},{},{},{}".format(bssid, channel, quality, dbm))
