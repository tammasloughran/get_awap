"""get_awap.py downloads AWAP data from the BoM and converts it to netcdf.
Usage: python get_awap.py ddmmyyyy-DDMMYYYY VAR

ddmmyyyy-DDMMYYYY - is the period to download

VAR - is the variable to download. Use either tmax, tmin, rain, 9amvapr, or 3pmvapr.

eg. python get_awap.py 01012015-31122015 tmax
"""
import urllib
import sys
if sys.version[0]=='3':
    urlretrieve = urllib.request.urlretrieve
elif sys.version[0]=='2':
    urlretrieve = urllib.urlretrieve
import numpy as np
import os
import pandas
from netCDF4 import Dataset
import datetime as dt

# Get args
args = sys.argv
period = args[1]
getvar = args[2]

# Check formatting of period
try:
    assert('-' in period)
    assert(type(int(period[:period.find('-')]))==int)
    assert(len(period[:period.find('-')])==8)
    assert(type(int(period[period.find('-')+1:]))==int)
    assert(len(period[period.find('-')+1:])==8)
except:
    print("Formatting of dates is incorrect. Dates format should be ddmmyyyy-DDMMYYYY")
    sys.exit(1)

# Manage dates
start = period[:period.find('-')]
end = period[period.find('-')+1:]
start_date = dt.datetime(int(start[4:]),int(start[2:4]), int(start[:2]))
end_date = dt.datetime(int(end[4:]),int(end[2:4]), int(end[:2]))
assert(start_date.year>=1900)
dates = pandas.date_range(start_date, end_date)

# Setup url strings
site = 'http://www.bom.gov.au/web03/ncc/www/awap/'
location = ''
getvar = args[2]
if getvar == 'tmin':
    location = 'temperature/minave/daily/grid/0.05/history/nat/'
elif getvar == 'tmax':
    location = 'temperature/maxave/daily/grid/0.05/history/nat/'
elif getvar == 'rain':
    location = 'rainfall/totals/daily/grid/0.05/history/nat/'
elif getvar == '9amvapr':
    location = 'vprp/vprph09/daily/grid/0.05/history/nat/'
elif getvar == '3pmvapr':
    location = 'vprp/vprph09/daily/grid/0.05/history/nat/'
else:
    print(getvar+' is not a valid variable. Use tmin, tmax, rain, 9amvapr, or 3pmvapr')

# Download
for idate in dates:
    cdate = idate.strftime('%Y%m%d')
    filename = cdate + cdate + '.grid.Z'
    if not os.path.exists(filename):
        url = site + location + filename
        urlretrieve(url, filename)
        os.system('uncompress '+filename)

# Load .grid files
for cyear in range(start_date.year, end_date.year+1):
    iday = 0
    this_year = dates[dates.year==cyear]
    days_in_year = (dates.year==cyear).sum()
    cdate = this_year[0]
    filename = cdate.strftime('%Y%m%d') + cdate.strftime('%Y%m%d') + '.grid'
    f = open(filename)
    cols = int(f.readline()[6:9])
    rows = int(f.readline()[6:9])
    first_lon = float(f.readline()[10:18])
    first_lat = float(f.readline()[10:18])
    delta = float(f.readline()[9:15])
    awap_data2 = np.ones((days_in_year,rows,cols))*np.nan
    for i, cday in enumerate(this_year):
        # Load
        cdate = cday.strftime('%Y%m%d')
        filename = cdate + cdate + '.grid'
        f = open(filename)
        cols = int(f.readline()[6:9])
        rows = int(f.readline()[6:9])
        awap_data = np.ones((rows,cols))*np.nan
        f.readline() # These lines are just the grid specification
        f.readline()
        f.readline()
        f.readline()
        for ix in range(rows):
            line = f.readline().split()
            awap_data[ix,:] = np.array([float(x) for x in line])
        awap_data2[i,...] = np.flipud(awap_data)
    # Save to file
    outfile = 'AWAP_'+getvar+'_'+this_year[0].strftime('%Y%m%d')+'-'+this_year[-1].strftime('%Y%m%d')+'.nc'
    ncdata = Dataset(outfile, 'w')
    setattr(ncdata, 'notes', 'Downloaded using get_awap https://github.com/tammasloughran/get_awap')
    times = [(this_year[i]-dt.datetime(1899,1,1)).days for i in range(this_year.size)]
    lats = [(int(first_lat*100)+i*int(delta*100))/100 for i in range(rows)]
    lons = [(int(first_lon*100)+i*int(delta*100))/100 for i in range(cols)]
    ncdata.createDimension('time',len(times))
    ncdata.createDimension('lat',rows)
    ncdata.createDimension('lon',cols)
    otime = ncdata.createVariable('time','float',dimensions=('time'))
    setattr(otime, 'standard_name', 'time')
    setattr(otime, 'calendar', 'proleptic_gregorian')
    setattr(otime, 'units', 'days since 1899-01-01 00:00:00')
    olat = ncdata.createVariable('lat','float',dimensions=('lat'))
    setattr(olat, 'standard_name', 'latitude')
    setattr(olat, 'long_name', 'Latitude')
    setattr(olat, 'units', 'degrees_north')
    setattr(olat, 'axis', 'Y')
    olon = ncdata.createVariable('lon','float',dimensions=('lon'))
    setattr(olon, 'standard_name', 'longitude')
    setattr(olon, 'long_name', 'Longitude')
    setattr(olon, 'units', 'degrees_east')
    setattr(olon, 'axis', 'X')
    odata = ncdata.createVariable(getvar,awap_data2.dtype,dimensions=('time','lat','lon'),fill_value=-99.99)
    if getvar=='tmax':
        setattr(odata, 'long_name', "Daily maximum temperature")
        setattr(odata, 'units', 'deg C')
    elif getvar=='tmin':
        setattr(odata, 'long_name', "Dialy minimum temperature")
        setattr(odata, 'units', 'deg C')
    elif getvar=='rain':
        setattr(odata, 'long_name', "Daily rainfall total")
        setattr(odata, 'units', 'kg m-2 d-1')
    otime[:] = times
    olat[:] = lats
    olon[:] = lons
    odata[:] = awap_data2
    ncdata.close()
