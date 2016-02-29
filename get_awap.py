"""get_awap.py downloads AWAP data from the BoM and converts it to netcdf.
Usage: python get_awap.py yyymmdd-YYYMMDD VAR

yyymmdd-YYYMMDD - is the period to download

VAR - is the variable to download. Use either tmax, tmin or rain.

eg. python get_awap.py 20150101-20160101 tmax
"""
import urllib
import sys
import numpy as np
import os
import pandas
from netCDF4 import Dataset

# Get args
args = sys.argv
period = args[1]
getvar = args[2]

# Manage dates
if not len(period)==17:
    print("Formatting of dates is incorrect. Dates format should be yyyymmdd-YYYYMMDD")
    sys.exit
start_date = period[:8]
end_date = period[9:]
start_year = int(start_date[:4])
end_year = int(end_date[:4])
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

# Download
for idate in dates:
    cdate = idate.strftime('%Y%m%d')
    filename = cdate + cdate + '.grid.Z'
    if not os.path.exists(filename):
        url = site + location + filename
        urllib.urlretrieve(url, filename)
        os.system('uncompress '+filename)

# Load .grid files
if start_year==end_year: end_year = end_year+1
for cyear in range(start_year, end_year):
    iday = 0
    this_year = dates[dates.year==cyear]
    days_in_year = (dates.year==cyear).sum()
    cdate = this_year[0].strftime('%Y%m%d')
    filename = cdate + cdate + '.grid'
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
    ncdata = Dataset('AWAP_'+getvar+'_%s.nc'%(cyear), 'w')
    strings = [x.strftime('%Y%m%d') for x in this_year]
    times = np.array([int(x) for x in strings])
    lats = np.arange(first_lat,first_lat+rows*delta,delta)
    lons = np.arange(first_lon,first_lon+cols*delta,delta)
    ncdata.createDimension('time',len(times))
    ncdata.createDimension('lat',rows)
    ncdata.createDimension('lon',cols)
    otime = ncdata.createVariable('time','float',dimensions=('time'))
    olat = ncdata.createVariable('lat','float',dimensions=('lat'))
    olon = ncdata.createVariable('lon','float',dimensions=('lon'))
    odata = ncdata.createVariable(getvar,awap_data2.dtype,dimensions=('time','lat','lon'))
    otime[:] = times
    olat[:] = lats
    olon[:] = lons[:-1]
    odata[:] = awap_data2
    ncdata.close()
