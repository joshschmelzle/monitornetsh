#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Monitors netsh's wlan interfaces, and converts signal quality to RSSI.

Tested with Windows 10 build 16299 and Python 3.6.4.
"""

__author__ = "Josh Schmelzle"
__version__ = "0.0.3"
__status__ = "Alpha"

import argparse
import logging
import logging.handlers
import os
import sys
import subprocess
import time
import traceback


class Interface:
    """netsh interface class to store data"""

    def __init__(
        self,
        name,
        mac,
        ssid,
        bssid,
        radio,
        auth,
        cipher,
        channel,
        receive,
        transmit,
        quality,
        rssi,
    ):
        self.name = name
        self.mac = mac
        self.ssid = ssid
        self.bssid = bssid
        self.radio = radio
        self.auth = auth
        self.cipher = cipher
        self.channel = channel
        self.receive = receive
        self.transmit = transmit
        self.quality = quality
        self.rssi = rssi


LOGGER = logging.getLogger("monitor_wlan")
LOGGER.setLevel(logging.INFO)

# write to rotating log files
if not os.path.exists("log"):
    os.mkdir("log")
LOG_DIR = os.path.join(os.getcwd(), "log")
LOG_FILE = "{}.log".format(os.path.basename(sys.argv[0]))
LOG_HANDLER = logging.handlers.TimedRotatingFileHandler(
    os.path.join(LOG_DIR, LOG_FILE), when="M", interval=2
)
LOG_HANDLER.setFormatter(
    logging.Formatter(
        "%(asctime)-.19s [%(levelname)s](%(funcName)s:%(lineno)d): %(message)s"
    )
)
LOG_HANDLER.setLevel(logging.INFO)
LOGGER.addHandler(LOG_HANDLER)

# log to console at a level determined by --verbose flag
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setLevel(
    logging.INFO
)  # set later by set_log_level_from_verbose() in interactive sessions
CONSOLE_HANDLER.setFormatter(
    logging.Formatter("[%(levelname)s](%(name)s): %(message)s")
)
LOGGER.addHandler(CONSOLE_HANDLER)

PARSER = argparse.ArgumentParser(
    description="Converts netsh.exe's Wi-Fi signal quality to RSSI.",
    epilog="Made with Python by {}".format(__author__),
    fromfile_prefix_chars="@",
)

PARSER.add_argument(
    "command",
    nargs="?",
    default="convert",
    help="command to execute",
    choices=["convert"],
)
PARSER.add_argument(
    "-V", "--version", action="version", version="%(prog)s {}".format(__version__)
)
PARSER.add_argument(
    "-v", "--verbose", action="count", help="verbosity level. repeat up to three times."
)
PARSER.add_argument(
    "-c", "--convert", action="store_true", help="returns dbm based on Netsh quality"
)
PARSER.add_argument(
    "-i", "--interval", help="polling interval for netsh.exe in seconds. default is 1."
)


def set_log_level_from_verbose(args):
    """set the log level"""
    if not args.verbose:
        CONSOLE_HANDLER.setLevel("ERROR")
    elif args.verbose == 1:
        CONSOLE_HANDLER.setLevel("WARNING")
    elif args.verbose == 2:
        CONSOLE_HANDLER.setLevel("INFO")
    elif args.verbose >= 3:
        CONSOLE_HANDLER.setLevel("DEBUG")
    else:
        LOGGER.critical("UNKNOWN NEGATIVE COUNT")


def get_function_name():
    """returns the calling function's name."""
    return traceback.extract_stack(None, 2)[0][2]


def convert_quality_to_dbm(quality):
    """ converts quality (percent) to dbm.

    conversion between quality (percentage) and dBm is as follows:
    `quality = 2 * (dbm + 100) where dBm: [-100 to -50]`
    `dbm = (quality / 2) - 100 where quality: [0 to 100]`
    https://docs.microsoft.com/en-us/windows/desktop/api/wlanapi/ns-wlanapi-_wlan_association_attributes
    """
    if quality <= 0:
        dbm = -100
    elif quality >= 100:
        dbm = -50
    else:
        dbm = (quality / 2) - 100
    return int(dbm)


def get_netsh_output():
    """gets and returns netsh output from netsh.exe"""
    LOGGER.debug("in <{}>".format(get_function_name()))
    try:
        netsh_output = subprocess.check_output(["netsh", "wlan", "show", "interface"])
        if args.verbose:
            LOGGER.info("{}".format(netsh_output))
        return netsh_output.decode("utf-8")
    except subprocess.CalledProcessError as ex:
        print("error getting netsh output")
        LOGGER.info(ex.returncode, ex.output)
        sys.exit(-1)


def parse_netsh_output(output):
    """extract and return data from netsh output"""
    LOGGER.debug("in <{}>".format(get_function_name()))

    ifaces = []
    name = ""
    mac = ""
    ssid = ""
    bssid = ""
    radio = ""
    auth = ""
    cipher = ""
    channel = ""
    receive = ""
    transmit = ""
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
                LOGGER.info("interface {} is not connected".format(name))
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
            receive = value
            continue
        if "transmit" in parameter:
            transmit = value
            continue
        if "signal" in parameter:
            quality = int(value.replace("%", ""))
            dbm = convert_quality_to_dbm(quality)
            ifaces.append(
                Interface(
                    name,
                    mac,
                    ssid,
                    bssid,
                    auth,
                    cipher,
                    radio,
                    channel,
                    receive,
                    transmit,
                    quality,
                    dbm,
                )
            )

    return ifaces


def poll():
    """handle conversion of Netsh quality to rssi value"""
    LOGGER.debug("in <{}>".format(get_function_name()))
    interfaces = parse_netsh_output(get_netsh_output())
    now = time.strftime("%Y%m%dt%H%M%S")
    if interfaces:
        for interface in interfaces:
            print(
                "[{}]:{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(
                    now,
                    interface.name,
                    interface.mac,
                    interface.ssid,
                    interface.bssid,
                    interface.radio,
                    interface.auth,
                    interface.cipher,
                    interface.channel,
                    interface.receive,
                    interface.transmit,
                    interface.quality,
                    interface.rssi,
                )
            )
            LOGGER.info(
                "{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(
                    interface.name,
                    interface.mac,
                    interface.ssid,
                    interface.bssid,
                    interface.radio,
                    interface.auth,
                    interface.cipher,
                    interface.channel,
                    interface.receive,
                    interface.transmit,
                    interface.quality,
                    interface.rssi,
                )
            )


def main(args):
    """
    sets up a scheduler
    """
    LOGGER.debug("in <{}>".format(get_function_name()))
    if args.interval is None:
        interval = 1
    else:
        interval = int(args.interval)

    print("netsh.exe polling interval: {}".format(interval))
    LOGGER.info("netsh.exe polling interval: {}".format(interval))
    print(
        "interface name, mac, ssid, bssid, radio, auth, cipher, channel, receive, transmit, quality, rssi"
    )
    LOGGER.info(
        "interface name, mac, ssid, bssid, radio, auth, cipher, channel, receive, transmit, quality, rssi"
    )
    starttime = time.time()
    while True:
        poll()
        time.sleep(interval - ((time.time() - starttime) % interval))


if __name__ == "__main__":
    try:
        args = PARSER.parse_args()
        set_log_level_from_verbose(args)
        LOGGER.info("{} {}".format(os.path.basename(sys.argv[0]), __version__))

        if args.command == "convert":
            main(args)
        else:
            LOGGER.error("fail: {}".format(args.command))
    except KeyboardInterrupt:
        LOGGER.critical("Stop requested by user...")
        sys.exit(-1)
    sys.exit(0)
