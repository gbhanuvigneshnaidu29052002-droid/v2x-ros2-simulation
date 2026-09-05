# Contributing to V2X Multi-Robot Autonomous Transportation System

Thank you for your interest in contributing to the V2X Multi-Robot Autonomous Transportation System! We welcome contributions from researchers, robotics developers, and the open-source community.

Please review this guide before submitting issues or pull requests.

---

## Code of Conduct

All contributors and maintainers must abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please report any unacceptable behavior to the project maintainers.

---

## Ways to Contribute

- **V2X Communication Protocols**: Implement ETSI ITS-G5 or IEEE 802.11p/CAM message structures, latency modeling, or packet-loss simulation.
- **Multi-Robot Coordination**: Enhance decentralized intersection management, platooning protocols, or dynamic auction-based parking spot allocation.
- **Traffic Simulation**: Expand the Gazebo smart city world (`v2x_city.world`) with pedestrian crosswalks, roundabout scenarios, or variable weather conditions.
- **Metrics & Telemetry**: Extend `perception_dashboard.py` with throughput graphs, inter-vehicle distance safety margins, or energy consumption estimators.

---

## Reporting Issues & Bugs

Please check existing [GitHub Issues](https://github.com/gbhanuvigneshnaidu29052002-droid/v2x-ros2-simulation/issues) before opening a new issue.

When creating a bug report, include:
1. **System Configuration**:
   - OS: Ubuntu 22.04 LTS
   - ROS 2 Distribution: Humble Hawksbill
   - Gazebo Version: Gazebo 11 Classic
2. **Reproduction Steps**: Complete launch commands used to trigger the bug.
3. **Observed vs. Expected Behavior**: Telemetry screenshots, collision timestamps, or topic communication drops.
4. **Terminal Logs**: Error traces from `robot_agent`, `traffic_light_controller`, or `emergency_manager`.

Please use the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md).

---

## Development Workflow

### 1. Fork & Clone
```bash
git clone https://github.com/<your-username>/v2x-ros2-simulation.git
cd v2x-ros2-simulation
```

### 2. Create a Topic Branch
```bash
git checkout -b feature/platooning-v2v-protocol
# or
git checkout -b fix/intersection-yield-lockout
```

### 3. Build & Source
```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

### 4. Run Multi-Robot Simulation Smoke Tests
```bash
# Terminal 1: Launch Gazebo world and all 4 agents
ros2 launch v2x_system multi_robot_v2x.launch.py

# Terminal 2: Verify telemetry dashboard
ros2 run v2x_system perception_dashboard
```

Verify that:
- `robot1` respects traffic light signals at the intersection.
- `ambulance` triggers emergency corridor clearance, causing civilian robots (`robot1`, `robot2`, `robot3`) to yield.
- `robot2` successfully queries and navigates to the assigned parking bay.

---

## Code Quality Standards

- **Python**: Follow PEP 8 style guidelines.
- **ROS 2 Concurrency**: Use multi-threaded executors where appropriate to avoid deadlocks between action clients and timer callbacks.
- **Git Hygiene**: Keep commits focused and atomic. Never commit `.ros/`, `.gazebo/`, `build/`, `install/`, or log files.

---

## Submitting a Pull Request

1. Fill out the [Pull Request Template](.github/pull_request_template.md).
2. Ensure `colcon build` succeeds without warnings.
3. Provide a simulation recording or screenshot of the dashboard confirming the change works as expected.

Thank you for helping build intelligent, safe multi-agent transportation infrastructure!
