# monitornetsh.py

This script monitor netsh.exe's connected wlan interface, and convert signal quality to a RSSI value. 

# requirements

a win32 machine with Python 3 installed.

tested with Python 3.6.4 and Windows 10 Enterprise (10.0.16299 N/A Build 16299).

# usage

by default the script will poll netsh.exe every second. use the `--interval` argument to change this. 

script will create subfolder called `log` where you will find rotating log files.

# sample output

```
>monitornetsh.py
netsh.exe polling interval: 1
interface name, mac, ssid, bssid, radio, auth, cipher, channel, receive, transmit, quality, rssi
[20181217t085334]:Internal WLAN NIC, 28:c6:3f:XX:XX:XX, eap, f0:5c:19:XX:XX:XX, WPA2-Enterprise, CCMP, 802.11n, 157, 300, 300, 99, -50
```

## 1 nic

![](https://github.com/joshschmelzle/netsh.exe_signal-quality_to_rssi/blob/master/quality-to-rssi-multiple-nic.png)

## multiple nics

![](https://github.com/joshschmelzle/netsh.exe_signal-quality_to_rssi/blob/master/quality-to-rssi-1-nic.png)

# conversion formula

conversion for signal quality (percentage) to RSSI (dBm) is based on how wlanSignalQuality is calculated from [Wlanapi.h](https://docs.microsoft.com/en-us/windows/desktop/api/wlanapi/ns-wlanapi-_wlan_association_attributes)

> A percentage value that represents the signal quality of the network. WLAN_SIGNAL_QUALITY is of type ULONG. This member contains a value between 0 and 100. A value of 0 implies an actual RSSI signal strength of -100 dbm. A value of 100 implies an actual RSSI signal strength of -50 dbm. You can calculate the RSSI signal strength value for wlanSignalQuality values between 1 and 99 using linear interpolation.

# license

project license can be found [here](https://github.com/joshschmelzle/netsh_quality_to_dbm/blob/master/LICENSE).
