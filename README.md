# monitornetsh

this script monitors netsh.exe's `netsh wlan show interfaces` to show connected WLAN information including the conversion of signal quality to an estimated Received Signal Strength Indicator (RSSI) value. 

# status

alpha

# known issues

this script relies on the data found in the output of `netsh wlan show interfaces`, and does not trigger a data refresh as it polls `netsh.exe`. this means that the signal quality and RSSI values are not frequently refreshed.

it's important to note that the signal quality found in the output of `netsh.exe` is a qualitative metric. 

this script uses linear interpolation to convert signal quality to RSSI. this means the RSSI reported by this script is not from the WLAN NIC driver.

## conversion formula

conversion for signal quality (percentage) to RSSI (dBm) is based on how `wlanSignalQuality` is calculated from [wlanapi.h](https://docs.microsoft.com/en-us/windows/desktop/api/wlanapi/ns-wlanapi-_wlan_association_attributes).

> A percentage value that represents the signal quality of the network. `WLAN_SIGNAL_QUALITY` is of type ULONG. This member contains a value between 0 and 100. A value of 0 implies an actual RSSI signal strength of -100 dbm. A value of 100 implies an actual RSSI signal strength of -50 dbm. You can calculate the RSSI signal strength value for wlanSignalQuality values between 1 and 99 using linear interpolation.

pseudo code for how this script calculates RSSI from signal quality:

```
// signal quality to RSSI
if(quality <= 0)
  rssi = -100;
else if(quality >= 100)
  rssi = -50;
else
  rssi = (quality / 2) - 100;
```

after reviewing the code above, you can see that this script cannot calculate RSSI better than -50. this may not be ideal depending on your needs.

you may be looking for a RSSI value reported by the driver such as available from the [wlanapi](https://docs.microsoft.com/en-us/windows/desktop/api/wlanapi/)). this script does not provide that.

# requirements

a win32 machine with Python v3.0+ installed.

tested with Python 3.6.4 and Windows 10 Enterprise (10.0.16299 N/A Build 16299).

# usage

by default the script will poll `netsh.exe` every second. use the `--interval` argument to change this. 

script will create subfolder in the current directory called `log` where you will find rotating log files.

# sample output

```
>monitornetsh.py
netsh.exe polling interval: 1
interface name, mac, ssid, bssid, radio, auth, cipher, channel, receive, transmit, quality, rssi
[20181217t085334]:Internal WLAN NIC, 28:c6:3f:XX:XX:XX, eap, f0:5c:19:XX:XX:XX, WPA2-Enterprise, CCMP, 802.11n, 157, 300, 300, 99, -50
```

## 1 nic

![](https://github.com/joshschmelzle/netsh.exe_signal-quality_to_rssi/blob/master/quality-to-rssi-multiple-nic.png)

## multiple nics (experimental)

![](https://github.com/joshschmelzle/netsh.exe_signal-quality_to_rssi/blob/master/quality-to-rssi-1-nic.png)

# credits

- [this stackoverflow answer](https://stackoverflow.com/questions/15797920/how-to-convert-wifi-signal-strength-from-quality-percent-to-rssi-dbm)
- [microsoft's wlanapi](https://docs.microsoft.com/en-us/windows/desktop/api/wlanapi/)

# license

project license can be found [here](https://github.com/joshschmelzle/netsh_quality_to_dbm/blob/master/LICENSE).
