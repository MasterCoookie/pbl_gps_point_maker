import math
from serial import Serial
import json


class Point:
    def __init__(self, x, y, address="TAG"):
        self.x = x
        self.y = y
        self.address = address
        self.is_observed = False

def gps_data_to_point(data):
    lat_raw = data[2]
    lat_deg = float(lat_raw[0:2])
    lat_min = float(lat_raw[2:])
    lat = lat_deg + (lat_min / 60)
    sign_lat = data[3]
    if sign_lat == "S":
        lat *= -1

    long_raw = data[4]
    long_deg = float(long_raw[0:3])
    long_min = float(long_raw[3:])
    long = long_deg + (long_min / 60)
    long_sign = data[5]
    if long_sign == "W":
        long *= -1

    return Point(lat, long)

def get_position():
    gps_serial = Serial("com10")
    while (True):
        try:
            line = str(gps_serial.readline(), encoding="ASCII")
            if "GPGGA" in line:
                data = line.split(',')
                # if (int(data[7]) > 0): #enough satellites
                return(gps_data_to_point(data))
        except(UnicodeDecodeError):
            pass
pos = get_position()

user_input = ""
points = []

while True:
    user_input = input("Please input device address, q to quit\n")
    if(user_input == "q"):
        break
    gps_point = get_position()
    point = {'x': gps_point.x, 'y': gps_point.y, "address": user_input}
    points.append(point)

points_json = json.dumps(points)

print(points_json)