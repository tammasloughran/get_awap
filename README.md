# get_awap
Get awap data

```
get_awap.py downloads AWAP data from the BoM and converts it to netcdf.

Usage: python get_awap.py ddmmyyyy-DDMMYYYY VAR

ddmmyyyy-DDMMYYYY - is the period to download

VAR - is the variable to download. Use either tmax, tmin, rain, 9amvapr, or 3pmvapr.

eg. python get_awap.py 01012015-31122015 tmax
```

Don't use awap data that's out at sea—it's nonsense. Same for central western Australia.
