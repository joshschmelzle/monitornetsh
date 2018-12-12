#!/usr/bin/env python3
#-*- coding: utf-8 -*-
"""
Gets signal quality from netsh.exe and converts it to rssi dbm.
"""
import sys
import subprocess

command = ['netsh', 'wlan', 'show', 'interface']
netsh_output = ""

class Interface():
    """
    netsh interface class
    """
    def __init__(self, name, mac, ssid, bssid, channel, quality, dbm):
        self.name = name
        self.mac = mac
        self.ssid = ssid
        self.bssid = bssid
        self.channel = channel
        self.quality = quality
        self.dbm = dbm

def convert(quality):
    """
    converts quality (percent) to dbm.
    """
    if quality <= 0:
        dbm = -100
    elif quality >= 100:
        dbm = -50
    else:
        dbm = (quality / 2) - 100
    return int(dbm)

try:
    netsh_output = subprocess.check_output(command)
except subprocess.CalledProcessError as ex:
    print("error getting netsh output")
    sys.exit(-1)

interfaces = []

netsh_output = netsh_output.decode("utf-8").lower()

name = ""
mac = ""
ssid = ""
bssid = ""
channel = ""
quality = ""

for i, line in enumerate(netsh_output.splitlines()):
    paramater = line.split(":", 1)[0].strip()
    try:
        value = line.split(":", 1)[1].strip()
    except IndexError:
        continue
    if "name" in paramater:
        name = value
    if "physical" in paramater:
        mac = value
    if "state" in paramater:
        state = value
        if "disconnect" in state:
            print("interface {} is not connected".format(name))
    if paramater == "ssid":
        ssid = value
    if "bssid" in paramater:
        bssid = value
    if "channel" in line:
        channel = value
    if "signal" in line:
        quality = int(value.replace("%", ""))
        dbm = convert(quality)
        interface = Interface(name, mac, ssid, bssid, channel, quality, dbm)
        interfaces.append(interface)

if interfaces:
    print("name, mac, ssid, bssid, channel, quality, dbm")
    for i in interfaces:
        print("{}, {}, {}, {}, {}, {}, {}".format(i.name, i.mac, i.ssid, i.bssid, i.channel, i.quality, i.dbm))
