# STE GPS
My BN-200 GPS library written in python
### How to use
    # to initialize library 
    # default: timezone = 0, baudrate=9600
    gps = Gps(serial_port, timezone, baudrate)     
    
    gps.fixed       # true if gps has fixed
    gps.position    # (latitude, longitude) tuple
    gps.latitude    # latitude value in degrees and minutes
    gps.longitde    # longitude value in meters    
    gps.altitude    # altitude value in degrees and minutes
    gps.speed       # ground speed value in km/h
    gps.satellites  # number of satellites used
    gps.timestamp   # timestamp dd-mm-yy hh:mm:ss
    gps.distance(x_latitude, x_longitude) # returns distance from point x