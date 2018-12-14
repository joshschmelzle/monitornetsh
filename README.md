# netsh.exe signal quality to rssi

convert netsh.exe's signal quality to a rssi value using python

# requirements

a win32 machine with Python 3 installed

# usage

by default the script will poll netsh.exe every second. use the `--interval` argument to change this. 

script will create rotating logs in a `log/` folder

# sample output

## 1 nic

![](https://github.com/joshschmelzle/netsh.exe_signal-quality_to_rssi/blob/master/quality-to-rssi-1-nic.png)

## multiple nics

![](https://github.com/joshschmelzle/netsh.exe_signal-quality_to_rssi/blob/master/quality-to-rssi-multiple-nic.png)

# conversion formula

conversion is based on how wlanSignalQuality is calculated from [Wlanapi.h](https://docs.microsoft.com/en-us/windows/desktop/api/wlanapi/ns-wlanapi-_wlan_association_attributes)

> A percentage value that represents the signal quality of the network. WLAN_SIGNAL_QUALITY is of type ULONG. This member contains a value between 0 and 100. A value of 0 implies an actual RSSI signal strength of -100 dbm. A value of 100 implies an actual RSSI signal strength of -50 dbm. You can calculate the RSSI signal strength value for wlanSignalQuality values between 1 and 99 using linear interpolation.

# license

project license can be found [here](https://github.com/joshschmelzle/netsh_quality_to_dbm/blob/master/LICENSE)
