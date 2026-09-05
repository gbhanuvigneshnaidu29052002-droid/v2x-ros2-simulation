---
name: Bug Report
about: Report a bug in multi-robot simulation, V2X messaging, or parking allocation
title: "[BUG] "
labels: ["bug"]
assignees: ""
---

## Description
A clear and concise description of the bug.

## Steps to Reproduce
1. Run `ros2 launch v2x_system multi_robot_v2x.launch.py`
2. Run `ros2 run v2x_system perception_dashboard`
3. Observe unexpected behavior at step '...'

## Expected Behavior
What should have occurred (e.g., robot stops at stop line on yellow/red light).

## Actual Behavior
What actually occurred (e.g., robot enters intersection during red signal, collision occurs).

## Console Logs / Error Traces
```text
Paste logs or terminal output here
```

## Telemetry / Screenshots
Attach terminal dashboard snapshots or Gazebo screenshots illustrating the issue.

## Environment Details
- **OS**: Ubuntu 22.04 LTS
- **ROS 2**: Humble Hawksbill
- **Gazebo**: Gazebo 11.10+
- **Python**: 3.10.x

## Additional Context
Add any other context about the problem here.
