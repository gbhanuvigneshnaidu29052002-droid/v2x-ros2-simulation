#!/usr/bin/env bash

WS="$HOME/v2x_task5_ws"
SETUP="cd $WS && source /opt/ros/humble/setup.bash && source install/setup.bash"

gnome-terminal \
  --tab --title="01 MAIN LAUNCH" -- bash -lc "$SETUP; export TURTLEBOT3_MODEL=burger; ros2 launch v2x_system multi_robot_v2x.launch.py; exec bash" \
  --tab --title="02 V2X TOPICS" -- bash -lc "$SETUP; sleep 5; ros2 topic list | grep v2x; exec bash" \
  --tab --title="03 ROS NODES" -- bash -lc "$SETUP; sleep 5; ros2 node list; exec bash" \
  --tab --title="04 TRAFFIC LIGHT" -- bash -lc "$SETUP; sleep 7; ros2 topic echo /v2x/traffic_light_state; exec bash" \
  --tab --title="05 EMERGENCY" -- bash -lc "$SETUP; sleep 7; ros2 topic echo /v2x/emergency_active; exec bash" \
  --tab --title="06 PARKING STATUS" -- bash -lc "$SETUP; sleep 7; ros2 topic echo /v2x/parking_status; exec bash" \
  --tab --title="07 PARKING ASSIGNMENT" -- bash -lc "$SETUP; sleep 7; ros2 topic echo /v2x/parking_assignment; exec bash" \
  --tab --title="08 PARKING FEEDBACK" -- bash -lc "$SETUP; sleep 7; ros2 topic echo /v2x/parking_feedback; exec bash" \
  --tab --title="09 ROBOT1 CMD" -- bash -lc "$SETUP; sleep 7; ros2 topic echo /robot1/cmd_vel; exec bash" \
  --tab --title="10 ROBOT2 CMD" -- bash -lc "$SETUP; sleep 7; ros2 topic echo /robot2/cmd_vel; exec bash" \
  --tab --title="11 AMBULANCE CMD" -- bash -lc "$SETUP; sleep 7; ros2 topic echo /ambulance/cmd_vel; exec bash"
