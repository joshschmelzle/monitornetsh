"""
retrieves signal quality from netsh.exe and converts it to rssi
"""
import subprocess
COMMAND = ['netsh', 'wlan', 'show', 'interface']
OUT = subprocess.check_output(COMMAND)
for line in OUT.decode("utf-8").lower().splitlines():
    paramater = line.split(":", 1)[0].strip()
    try:
        value = line.split(":", 1)[1].strip()
    except IndexError:
        continue
    if "signal" in line:
        quality = int(value.replace("%", ""))
        if quality <= 0:
            dbm = -100
        elif quality >= 100:
            dbm = -50
        else:
            dbm = (quality / 2) - 100
        dbm = int(dbm)
        print("quality,dbm")
        print("{},{}".format(quality, dbm))
