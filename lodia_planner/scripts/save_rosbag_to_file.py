#!/usr/bin/env python3

import rospy
from std_msgs.msg import Float32MultiArray
from grid_map_msgs.msg import GridMap
from sensor_msgs.msg import CompressedImage
from series_elastic_actuator_msgs.msg import SeActuatorReadings
from any_msgs.msg import ExtendedJointState
from anymal_msgs.msg import AnymalState
import numpy as np
import csv
from datetime import datetime
import os


data_list_a_drive = [[] for _ in range(12)]
data_list_t_drive = [[] for _ in range(12)]
data_list_a_stateesti = [[] for _ in range(12)]
data_list_phi_stateesti = [[] for _ in range(12)]
data_list_t_stateesti = [[] for _ in range(12)]
data_list_footprint = [[] for _ in range(4)]
data_list_feetcenter = [[] for _ in range(4)]
data_list_feetpositions = [[] for _ in range(12)]
data_list_feetcontact = [[] for _ in range(4)]
data_list_twist = [[] for _ in range(3)]

def message_callback_drive(msg):
    global data_list_a_drive, data_list_t_drive
    for i, reading in enumerate(msg.readings):
        data_list_a_drive[i].append(reading.state.joint_acceleration)
        data_list_t_drive[i].append(reading.state.joint_torque)


def message_callback_stateestimator(msg):
    global data_list_a_stateesti, data_list_t_stateesti, data_list_phi_stateesti
    # for i, reading in enumerate(msg.acceleration):
    #     data_list_a_stateesti[i].append(reading)
    for i, reading in enumerate(msg.effort):
        data_list_t_stateesti[i].append(reading)
    for i, reading in enumerate(msg.position):
        data_list_phi_stateesti[i].append(reading)


def message_callback_footreadings(msg):
    global data_list_footprint, data_list_feetcenter, data_list_twist

    data_list_footprint[0].append(msg.frame_transforms[0].transform.rotation.x)
    data_list_footprint[1].append(msg.frame_transforms[0].transform.rotation.y)
    data_list_footprint[2].append(msg.frame_transforms[0].transform.rotation.z)
    data_list_footprint[3].append(msg.frame_transforms[0].transform.rotation.w)

    data_list_feetcenter[0].append(msg.frame_transforms[1].transform.rotation.x)
    data_list_feetcenter[1].append(msg.frame_transforms[1].transform.rotation.y)
    data_list_feetcenter[2].append(msg.frame_transforms[1].transform.rotation.z)
    data_list_feetcenter[3].append(msg.frame_transforms[1].transform.rotation.w)

    for i, reading in enumerate(msg.contacts):
        data_list_feetpositions[3*i].append(reading.position.x)
        data_list_feetpositions[3*i+1].append(reading.position.y)
        data_list_feetpositions[3*i+2].append(reading.position.z)
        data_list_feetcontact[i].append(reading.state)

    data_list_twist[0].append(msg.twist.twist.linear.x)
    data_list_twist[1].append(msg.twist.twist.linear.y)
    data_list_twist[2].append(msg.twist.twist.linear.z)


def save_data():
    # global data_list_a_stateesti, data_list_t_stateesti
    # global data_list_a_drive, data_list_t_drive
    # global data_list_footprint, data_list_feetcenter
    global data_list_phi_stateesti, data_list_t_stateesti
    global data_list_feetpositions, data_list_feetcontact, data_list_twist

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    header = ['LF_HAA', 'LF_HFE', 'LF_KFE', 'RF_HAA', 'RF_HFE', 'RF_KFE', 'LH_HAA', 'LH_HFE', 'LH_KFE', 'RH_HAA', 'RH_HFE', 'RH_KFE']
    folder_path = os.path.join(os.getcwd(), timestamp)
    os.makedirs(folder_path, exist_ok=True)

    # # Data from actuator readings
    # csv_file_name = f'joint_acceleration_drive.csv'
    # file_path = os.path.join(folder_path, csv_file_name)
    # with open(file_path, mode='w', newline='') as csv_file:
    #     csv_writer = csv.writer(csv_file)
    #     csv_writer.writerow([f'Value {i+1}' for i in range(12)])
    #     for row in zip(*data_list_a_drive):
    #         csv_writer.writerow(row)

    # csv_file_name = f'joint_torque_drive.csv'
    # file_path = os.path.join(folder_path, csv_file_name)
    # with open(file_path, mode='w', newline='') as csv_file:
    #     csv_writer = csv.writer(csv_file)
    #     csv_writer.writerow([f'Motor {i+1}' for i in range(12)])  
    #     for row in zip(*data_list_t_drive):
    #         csv_writer.writerow(row)

    # # Actuator data from state estimator
    # csv_file_name = f'joint_acceleration_stateestimator.csv'
    # file_path = os.path.join(folder_path, csv_file_name)
    # with open(file_path, mode='w', newline='') as csv_file:
    #     csv_writer = csv.writer(csv_file)
    #     csv_writer.writerow([i for i in header]) 
    #     for row in zip(*data_list_a_stateesti):
    #         csv_writer.writerow(row)

    # # Foot state data from state estimator
    # csv_file_name = f'footprint.csv'
    # file_path = os.path.join(folder_path, csv_file_name)
    # with open(file_path, mode='w', newline='') as csv_file:
    #     csv_writer = csv.writer(csv_file)
    #     csv_writer.writerow(['x','y','z','w']) 
    #     for row in zip(*data_list_footprint):
    #         csv_writer.writerow(row)

    # csv_file_name = f'feetcenter.csv'
    # file_path = os.path.join(folder_path, csv_file_name)
    # with open(file_path, mode='w', newline='') as csv_file:
    #     csv_writer = csv.writer(csv_file)
    #     csv_writer.writerow(['x','y','z','w'])  
    #     for row in zip(*data_list_feetcenter):
    #         csv_writer.writerow(row)

    ######## EVERYTHING AFTER HERE IS NEEDED FOR ENERGY ESTIMATION ########
    # csv_file_name = f'joint_torque_stateestimator.csv'
    # file_path = os.path.join(folder_path, csv_file_name)
    # with open(file_path, mode='w', newline='') as csv_file:
    #     csv_writer = csv.writer(csv_file)
    #     csv_writer.writerow([i for i in header])  
    #     for row in zip(*data_list_t_stateesti):
    #         csv_writer.writerow(row)

    # csv_file_name = f'joint_orientation_stateestimator.csv'
    # file_path = os.path.join(folder_path, csv_file_name)
    # with open(file_path, mode='w', newline='') as csv_file:
    #     csv_writer = csv.writer(csv_file)
    #     csv_writer.writerow([i for i in header])  
    #     for row in zip(*data_list_phi_stateesti):
    #         csv_writer.writerow(row)

    # csv_file_name = f'feet_position.csv'
    # header = ['LF x', 'LF y', 'LF z', 'RF x', 'RF y', 'RF z', 'LH x', 'LH y', 'LH z', 'RH x', 'RH y', 'RH z']
    # file_path = os.path.join(folder_path, csv_file_name)
    # with open(file_path, mode='w', newline='') as csv_file:
    #     csv_writer = csv.writer(csv_file)
    #     csv_writer.writerow([i for i in header])  
    #     for row in zip(*data_list_feetpositions):
    #         csv_writer.writerow(row)

    # csv_file_name = f'feet_contact.csv'
    # header = ['LF', 'RF', 'LH', 'RH']
    # file_path = os.path.join(folder_path, csv_file_name)
    # with open(file_path, mode='w', newline='') as csv_file:
    #     csv_writer = csv.writer(csv_file)
    #     csv_writer.writerow([i for i in header])  
    #     for row in zip(*data_list_feetcontact):
    #         csv_writer.writerow(row)

    csv_file_name = f'twist.csv'
    header = ['x', 'y', 'z']
    #file_path = os.path.join(folder_path, csv_file_name)
    with open(csv_file_name, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([i for i in header])  
        for row in zip(*data_list_twist):
            csv_writer.writerow(row)


if __name__ == "__main__":
    rospy.init_node("save_files_node")
    rospy.Subscriber('/anymal_low_level_controller/actuator_readings', SeActuatorReadings, message_callback_drive)
    rospy.Subscriber('/state_estimator/joint_states', ExtendedJointState, message_callback_stateestimator)
    rospy.Subscriber('/state_estimator/anymal_state', AnymalState, message_callback_footreadings)

    # Save data in numpy array
    rospy.on_shutdown(save_data) 

    rospy.spin()