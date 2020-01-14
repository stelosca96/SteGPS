from gps import Gps
from time import sleep


def print_gps():
    if not gps.fixed:
        print("GPS not fixed")
        return
    print("\n---------------------------------")
    print("Satellites: ", gps.satellites)
    print("Timestamp: ", gps.timestamp)
    print("Time: ", gps.time)
    print("Date: ", gps.date)
    print("Position: ", gps.position)
    print("Latitude: ", gps.latitude, "°")
    print("Longitude: ", gps.longitude, "°")
    print("Altitude: ", gps.altitude, "m")
    print("Speed: ", gps.speed, "km/h")
    print("---------------------------------\n")


gps = Gps('/dev/ttyAMA1', 9600)
while True:
    print_gps()
    sleep(2)
