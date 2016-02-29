# get_awap
Get awap data

The Bureau of Meteorology provide a data set called AWAP, which is statistically interpolated station data for Australia. 
It's great because anyone can go to the BoM website, make figures and download it, all for free. 
While this is useful for teachers and making simple figures, if you're a researcher, it's an unwieldy, terrible, and pretty dumb way of distributing it.
It's in an archived text format so it takes up a ridiculous amount of space.
And you have to manually load text files into whatever analysis software you are using.
The text format is only really useful for something like excel, and if you're using excel to study geospatial data, shame on you.
There were a few scripts floating around my research institution that downloaded the data, converted it to netCDF and regridded it to a different resolution, but they all sucked. 
(And by that I mean they were written in a programming language I didn't understand so if they didn’t work—which they didn't—or I had to change something—which I did—I had to learn a whole new programming language to get them working—which is bullshit.)
So, this script downloads awap and converts it to netCDF format—minus regridding because there's already CDO to do that sort of stuff.

Don't use awap data that's out at sea—it's nonsense. Same for central western Australia.
