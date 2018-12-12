# netsh.exe signal quality to dbm converter

Convert netsh.exe's signal quality to a dbm value using Python

# requirements

a win32 machine with Python 3 installed

# how the conversion is calculated

Conversion is based on how wlanSignalQuality is calculated from [Wlanapi.h](https://docs.microsoft.com/en-us/windows/desktop/api/wlanapi/ns-wlanapi-_wlan_association_attributes)

# sample output

![](https://github.com/joshschmelzle/netsh_quality_to_dbm/blob/master/quality_to_dbm_simple.png)

# license

project license can be found [here](https://github.com/joshschmelzle/netsh_quality_to_dbm/blob/master/LICENSE)
