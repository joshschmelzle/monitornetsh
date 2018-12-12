#!/usr/bin/env python3
#-*- coding: utf-8 -*-
"""
Gets signal quality from netsh.exe and converts it to rssi dbm.
"""
import sys
import subprocess

class Interface():
    """
    netsh interface class to store data
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

def get_netsh_output(command):
    """
    return output from netsh.exe
    """
    try:
        netsh_output = subprocess.check_output(command)
    except subprocess.CalledProcessError:
        print("error getting netsh output")
        sys.exit(-1)

    return(netsh_output.decode("utf-8").lower())

def start():
    """
    main function
    """
    output = get_netsh_output(['netsh', 'wlan', 'show', 'interface'])

    interfaces = []
    name = ""
    mac = ""
    ssid = ""
    bssid = ""
    channel = ""
    quality = ""

    for i, line in enumerate(output.splitlines()):
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
            interfaces.append(Interface(name, mac, ssid, bssid, channel, quality, dbm))

    if interfaces:
        print("name, mac, ssid, bssid, channel, quality, dbm")
        for i in interfaces:
            print("{}, {}, {}, {}, {}, {}, {}".format(i.name, i.mac, i.ssid, i.bssid, i.channel, i.quality, i.dbm))

if __name__ == '__main__':
    try:
        start()
    except KeyboardInterrupt:
        print("KeyboardInterrupt: stop requested...")
