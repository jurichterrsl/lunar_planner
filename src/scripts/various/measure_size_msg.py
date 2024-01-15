#!/usr/bin/env python3

import rospy
from std_msgs.msg import Float32MultiArray
from grid_map_msgs.msg import GridMap
from sensor_msgs.msg import CompressedImage
import numpy as np


def callback_elevationmap(msg):
    print(len(msg.data[0].layout.dim))
    print(msg.data[0].layout.dim[0].label)
    print(msg.data[0].layout.dim[0].size)
    print(msg.data[0].layout.dim[0].stride)
    print(msg.data[0].layout.dim[1].label)
    print(msg.data[0].layout.dim[1].size)
    print(msg.data[0].layout.dim[1].stride)


def callback_image(msg):
    sizes.append(len(msg.data))
    print(max(sizes))


if __name__ == "__main__":
    rospy.init_node("message_size_listener")

    # # Elevation map
    # topic_name = "/elevation_mapping/elevation_map_recordable"
    # rospy.Subscriber(topic_name, GridMap, callback_elevationmap) map

    # Image
    global sizes
    sizes = []
    topic_name = "/wide_angle_camera_rear/image_color_rect/compressed"
    rospy.Subscriber(topic_name, CompressedImage, callback_image)

    rospy.spin()