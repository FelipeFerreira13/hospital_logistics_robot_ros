# Hospital Logistics Robot - ROS 1

ROS 1 project for an autonomous mobile robot designed to operate in a hospital logistics environment.  
The robot is able to navigate through a hospital-like arena, read a work order board, identify medicine cubes, HazMat cubes and patient gurneys, and transport them between dispensary areas, patient rooms, gurney pads and decontamination locations.

The robot uses a three omni-wheel mobile base for holonomic movement and an Object Management System (OMS) for manipulating medicine boxes and patient gurneys.

<img width="1112" height="562" alt="image" src="https://github.com/user-attachments/assets/20af8de4-b3da-41d4-ad74-4bfd00795527" />



Project Documentation: https://drive.google.com/file/d/1miT9k_YCgWma2GB6V60KPX5w_I7PBsBJ/view?usp=sharing

Testing and Validation:
- https://www.youtube.com/watch?v=wKqr0rEgRGI&t=407s
- https://www.youtube.com/watch?v=o8iod3cifyY&t=14s
## Dependencies

This project was developed for ROS 1 and VMX-Pi-based robot control.

Recommended setup:

- Operating System: Ubuntu 20.04 LTS
- ROS Version: ROS Noetic
- Build System: catkin
- Python Version: Python 3
- C++ Compiler: GCC / G++
- Hardware Platform: Raspberry Pi 4 with Studica VMX-Pi, or Ubuntu PC for development

ROS pkgs:

- geometry_msgs
- nav_msgs
- sensor_msgs
- tf
- robot_state_publisher
- joint_state_publisher
- xacro
- move_base
- move_base_msgs
- global_planner
- teb_local_planner
- laser_filters
- cv_bridge
- image_transport
- dynamic_reconfigure
- ydlidar_ros_driver

## Project Overview

The system is based on the following main robot functions:

- Autonomous navigation in a hospital-like environment
- Work order board recognition using computer vision
- Medicine cube and HazMat cube identification
- Gurney detection and handling
- Object pickup and delivery using the OMS
- Sensor-based position referencing
- ROS-based integration with VMX-Pi hardware

<img width="1813" height="2099" alt="hospital_robot_diagram" src="https://github.com/user-attachments/assets/c18429eb-b8d5-4233-9dda-07e2bf911335" />


## Robot Platform

The robot is composed of two main mechanical subsystems:

### Mobile Base

The mobility system uses three omni wheels positioned at 120 degrees from each other.  
This configuration allows the robot to move forward, backward, sideways, diagonally and rotate, making it suitable for narrow hospital-like paths and precise alignment with rooms, stands and pads.

### Object Management System

The OMS is responsible for handling the objects required by the task. It includes:

- Vertical movement for reaching different cube heights
- Gripper actuation for cubes and gurneys
- Limit switch referencing
- Servo-controlled manipulation
- Encoder-based elevator feedback

The OMS is used to collect, store, lift and deliver medicine cubes, HazMat cubes and patient gurneys.

## ROS 1 Packages

The project is organized as a ROS 1 catkin workspace with the following packages:

```text
src/
├── base_controller/
├── camera/
├── core/
├── odometry/
├── oms/
├── robot/
└── vmxpi_ros/ 
```

- **base_controller**: handles robot movement. It connects the robot either to the ROS Navigation Stack through move_base or to a simple custom movement controller used for direct position correction.
- **camera**: contains computer vision routines. It uses Python and OpenCV to read the order board, detect colored cubes, detect stands, and assist the robot during visual alignment.
- **core**: is the high-level mission controller. It coordinates the complete task execution by calling movement, camera, OMS, and odometry services.
- **odometry**: estimates and publishes the robot position using wheel velocity information and the NavX gyroscope.
- **oms**: controls the Object Management System, including elevator height control, gripper actuation, and limit switch referencing.
- **robot**: contains the robot description, TF configuration, RViz setup, Lidar launch files, costmap parameters, and local planner configuration.
- **vmxpi_ros**: rovides the hardware interface between ROS and the Studica VMX-Pi ecosystem.

