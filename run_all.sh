#!/bin/bash
cd ~/capston_h3c_integration
./clean_before_launch.sh
source install/setup.bash
ros2 launch capston_bringup bringup_all.launch.py