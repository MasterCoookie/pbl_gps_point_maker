import math
from serial import Serial
from scipy.spatial import distance_matrix
import numpy as np
import json
import pandas as pd
GPS_LIMIT = 120
ENABLE_DEBUG_LOGS = True

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
    lat = round(lat, 6)

    long_raw = data[4]
    long_deg = float(long_raw[0:3])
    long_min = float(long_raw[3:])
    long = long_deg + (long_min / 60)
    long_sign = data[5]
    if long_sign == "W":
        long *= -1
    long = round(long, 6)    

    return Point(lat, long)

def get_position(com_port:str,user_input:str):
    positions = []
    gps_serial = Serial(com_port)
    
    while len(positions) < GPS_LIMIT:
        try:
            line = str(gps_serial.readline(), encoding="ASCII")
            if "GPGGA" in line:
                data = line.split(',')
                if (int(data[7]) > 0): #enough satellites
                    print(len(positions))
                    positions.append((gps_data_to_point(data)))
                else:
                    print("Not enough satelites", data[7])
        except(UnicodeDecodeError):
            print("UnicodeDecodeError!")
    
    x_list = []
    y_list = []
    
    for pos in positions:
        x_list.append(pos.x)
        y_list.append(pos.y)
    if ENABLE_DEBUG_LOGS:
        with open("./data/debug_logs_"+user_input+".txt", "w+") as f:
            for i in range(GPS_LIMIT):
                f.write(f"#{i} x:{x_list[i]} y:{y_list[i]}")
    df = pd.DataFrame(list(zip(x_list, y_list)),
           columns =['x', 'y'])
    
    df.to_csv("./data/"+user_input+".csv")
    x_list.sort()
    y_list.sort()   
    return Point(x_list[int(GPS_LIMIT/2)], y_list[int(GPS_LIMIT/2)])

def get_medioid_index(df: pd.DataFrame)->int:
    m = distance_matrix(df.values, df.values)
    i = np.argmin(m.sum(axis=0))
    return i
    
def read_json_gps_points():
    f = open('GPSdata.json')
    return json.load(f)

if __name__ == "__main__":
    
    user_input = ""
    points = []

    com_port = input("Please inpunt serial path\n")

    while True:
        user_input = input("Please input device address, q to quit\n")
        if(user_input == "q"):
            break
        gps_point = get_position(com_port,user_input)
        point = {'x': gps_point.x, 'y': gps_point.y, "address": user_input}
        points.append(point)

    points_json = json.dumps(points, indent=3)

    with open('GPSdata.json', 'w') as outfile:
        outfile.write(points_json)
        

    print(points_json)