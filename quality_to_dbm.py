#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gets and converts netsh.exe's signal quality to a RSSI value
"""

__author__ = "Josh Schmelzle"
__version__ = "0.0.2"
__status__ = "Alpha"

import argparse
import logging
import logging.handlers
import os
import sys
import subprocess
import time

class Interface():
    """
    netsh interface class to store data
    """
    def __init__(self, name, mac, ssid, bssid, radio, auth, cipher, channel, rx, tx, quality, rssi):
        self.name = name
        self.mac = mac
        self.ssid = ssid
        self.bssid = bssid
        self.radio = radio
        self.auth = auth
        self.cipher = cipher
        self.channel = channel
        self.rx = rx
        self.tx = tx
        self.quality = quality
        self.rssi = rssi

logger = logging.getLogger('quality-to-rssi')
logger.setLevel(logging.INFO)

# write to rotating log files
if not os.path.exists('log'):
    os.mkdir('log')
log_handler = logging.handlers.TimedRotatingFileHandler('log/{}.log'.format(os.path.basename(sys.argv[0])), when='M', interval=2)
log_handler.setFormatter(logging.Formatter('%(asctime)-.19s [%(levelname)s](%(name)s:%(funcName)s:%(lineno)d): %(message)s'))
log_handler.setLevel(logging.INFO)
logger.addHandler(log_handler)

# log to console at a level determined by --verbose flag
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO) # set later by set_log_level_from_verbose() in interactive sessions
console_handler.setFormatter(logging.Formatter('[%(levelname)s](%(name)s): %(message)s'))
logger.addHandler(console_handler)

parser = argparse.ArgumentParser(
    description="Converts netsh.exe's Wi-Fi signal quality to RSSI.",
    epilog="Made with Python by {}".format(__author__),
    fromfile_prefix_chars='@'
    )

parser.add_argument('command', nargs="?", default="convert", help="command to execute", choices=['convert'])
parser.add_argument('-V', '--version', action="version", version="%(prog)s {}".format(__version__))
parser.add_argument('-v', '--verbose', action="count", help="verbosity level. repeat up to three times.")
parser.add_argument('-c', '--convert', action="store_true", help="returns dbm based on Netsh quality")
parser.add_argument('-i', '--interval', help="polling interval for netsh.exe in seconds. default is 1.")

def set_log_level_from_verbose(args):
    """
    sets the log level
    """
    if not args.verbose:
        console_handler.setLevel('ERROR')
    elif args.verbose == 1:
        console_handler.setLevel('WARNING')
    elif args.verbose == 2:
        console_handler.setLevel('INFO')
    elif args.verbose >= 3:
        console_handler.setLevel('DEBUG')
    else:
        logger.critical("UNKNOWN NEGATIVE COUNT")

def function_name():
    """
    returns the calling functions name.
    """
    import traceback
    return traceback.extract_stack(None, 2)[0][2]

def get_netsh_output():
    """
    gets and returns netsh output from netsh.exe
    """
    logger.debug("in <{}>".format(function_name()))
    try:
        netsh_output = subprocess.check_output(['netsh', 'wlan', 'show', 'interface'])
        if args.verbose:
            logger.info("{}".format(netsh_output))
        return(netsh_output.decode("utf-8"))
    except subprocess.CalledProcessError as ex:
        print("error getting netsh output")
        logger.info(ex.returncode, ex.output)
        sys.exit(-1)

def convert_quality_to_dbm(quality):
    """
    converts quality (percent) to dbm.

    A percentage value that represents the signal quality of the netpoll. WLAN_SIGNAL_QUALITY is of type ULONG. This member contains a value between 0 and 100. A value of 0 implies an actual dbm signal strength of -100 dbm. A value of 100 implies an actual dbm signal strength of -50 dbm. You can calculate the dbm signal strength value for wlanSignalQuality values between 1 and 99 using linear interpolation.
    https://docs.microsoft.com/en-us/windows/desktop/api/wlanapi/ns-wlanapi-_wlan_association_attributes

    conversion between quality (percentage) and dBm is as follows:
    `quality = 2 * (dbm + 100) where dBm: [-100 to -50]`
    `dbm = (quality / 2) - 100 where quality: [0 to 100]`
    """
    if quality <= 0:
        dbm = -100
    elif quality >= 100:
        dbm = -50
    else:
        dbm = (quality / 2) - 100
    return int(dbm)

def get_data_from_netsh_output(output):
    """
    extract and return data from netsh output
    """
    logger.debug("in <{}>".format(function_name()))

    ifaces = []
    name = ""
    mac = ""
    ssid = ""
    bssid = ""
    radio = ""
    auth = ""
    cipher = ""
    channel = ""
    rx = ""
    tx = ""
    quality = ""

    for line in output.splitlines():
        parameter = line.split(":", 1)[0].strip().lower()
        try:
            value = line.split(":", 1)[1].strip()
        except IndexError:
            continue
        if "name" in parameter:
            name = value
            continue 
        if "state" in parameter:
            if value == "disconnected":
                print("{} state is disconnected".format(name))
                break
            continue 
        if "physical" in parameter:
            mac = value
            continue 
        if "state" in parameter:
            state = value
            if "disconnect" in state.lower():
                logger.info("interface {} is not connected".format(name))
            continue 
        if parameter == "ssid":
            ssid = value
            continue 
        if "bssid" in parameter:
            bssid = value
            continue 
        if "authentication" in parameter:
            auth = value
            continue 
        if "cipher" in parameter:
            cipher = value
            continue 
        if "radio" in parameter:
            radio = value
            continue 
        if "channel" in parameter:
            channel = value
            continue 
        if "receive" in parameter:
            rx = value
            continue 
        if "transmit" in parameter:
            tx = value
            continue 
        if "signal" in parameter:
            quality = int(value.replace("%", ""))
            dbm = convert_quality_to_dbm(quality)
            ifaces.append(Interface(name, mac, ssid, bssid, auth, cipher, radio, channel, rx, tx, quality, dbm))

    return(ifaces)

def poll():
    """
    handle conversion of Netsh quality to rssi value
    """
    logger.debug("in <{}>".format(function_name()))
    interfaces = get_data_from_netsh_output(get_netsh_output())
    now = time.strftime("%H%M%S")
    if interfaces:
        for i in interfaces:
            print("{}:{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(now, i.name, i.mac, i.ssid, i.bssid, i.radio, i.auth, i.cipher, i.channel, i.rx, i.tx, i.quality, i.rssi))
            logger.info("{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(i.name, i.mac, i.ssid, i.bssid, i.radio, i.auth, i.cipher, i.channel, i.rx, i.tx, i.quality, i.rssi))
    
def setup_loop(args):
    """
    sets up a scheduler
    """
    logger.debug("in <{}>".format(function_name()))
    if args.interval is None:
        interval = 1
    else:
        interval = int(args.interval)
    
    print("netsh.exe polling interval: {}".format(interval))
    print("interface name, mac, ssid, bssid, radio, auth, cipher, channel, rx, tx, quality, rssi")
    starttime = time.time()
    while True:
        poll()
        time.sleep(interval - ((time.time() - starttime) % interval))

if __name__ == '__main__':
    try:
        args = parser.parse_args()
        set_log_level_from_verbose(args)
        logger.info("{} {}".format(os.path.basename(sys.argv[0]), __version__))

        if args.command == 'convert':
            setup_loop(args)
        else:
            logger.error("fail: {}".format(args.command))
    except KeyboardInterrupt:
        logger.critical("Stop requested by user...")
        sys.exit(-1)
    sys.exit(0)
