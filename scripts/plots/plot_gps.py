#!/usr/bin/env python3
import matplotlib
matplotlib.use('TkAgg')  # Set the backend explicitly before importing pyplot

import rospy
from sensor_msgs.msg import NavSatFix
import matplotlib.pyplot as plt
from geometry_msgs.msg import PointStamped
import numpy as np
import math


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth's radius in meters
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi_1) * math.cos(phi_2) * \
        math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def plot_lla_callback(msg):
    x_vals_lla.append(msg.longitude)
    y_vals_lla.append(msg.latitude)
    lon1 = x_vals_lla[len(x_vals_lla)-1]
    lon2 = x_vals_lla[len(x_vals_lla)-2]
    lat1 = y_vals_lla[len(y_vals_lla)-1]
    lat2 = y_vals_lla[len(y_vals_lla)-2]
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    if distance>0.2:
        print("LLA", distance)

def plot_ecef_callback(msg):
    x_vals.append(msg.point.x)
    y_vals.append(msg.point.y)
    z_vals.append(msg.point.z)
    dx = x_vals[len(x_vals)-1] - x_vals[len(x_vals)-2]
    dy = y_vals[len(y_vals)-1] - y_vals[len(y_vals)-2]
    dz = z_vals[len(z_vals)-1] - z_vals[len(z_vals)-2]
    distance = np.sqrt(dx**2+dy**2+dz**2)

    if distance > 0.15:
        print("ECEF", distance)
    # Distance new point from average
    if len(x_vals)>11:
        x_avg = sum(x_vals[len(x_vals)-12:len(x_vals)-2])/10
        y_avg = sum(y_vals[len(y_vals)-12:len(y_vals)-2])/10
        z_avg = sum(z_vals[len(z_vals)-12:len(z_vals)-2])/10
        diff_new = np.sqrt((x_vals[len(x_vals)-1] - x_avg)**2 +
                        (y_vals[len(y_vals)-1] - y_avg)**2 +
                        (z_vals[len(z_vals)-1] - z_avg)**2)
        if diff_new > 0.5:
            print("Distance new point to avg  ", diff_new)

def plot_ecef_callback2(msg):
    x_vals.append(msg.point.x)
    y_vals.append(msg.point.y)
    z_vals.append(msg.point.z)
    # dx = x_vals[len(x_vals)-1] - x_vals[len(x_vals)-2]
    # dy = y_vals[len(y_vals)-1] - y_vals[len(y_vals)-2]
    # dz = z_vals[len(z_vals)-1] - z_vals[len(z_vals)-2]
    # distance = np.sqrt(dx**2+dy**2+dz**2)
    if len(x_vals) == 300:
        plt.figure()
        plt.plot(x_vals)
        plt.figure()
        plt.plot(y_vals)
        plt.figure()
        plt.plot(z_vals)
        plt.show()
        x_vals.clear()
        y_vals.clear()
        z_vals.clear()


if __name__ == '__main__':
    rospy.init_node("plotter")
    global x_vals, y_vals, z_vals
    x_vals = []
    y_vals = []
    z_vals = []
    global x_vals_lla, y_vals_lla, z_vals_lla
    x_vals_lla = []
    y_vals_lla = []
    z_vals_lla = []

    # rospy.Subscriber('/rtk_gps_driver/position_receiver_0/ros/navsatfix',
    #                                     NavSatFix, plot_lla_callback)
    rospy.Subscriber('/rtk_gps_driver/position_receiver_0/ros/pos_ecef',
                                        PointStamped, plot_ecef_callback)

    # plt.ion()
    # plt.show()
    rospy.spin()

