## Summary

Please summarize the purpose of this PR and what problem or feature it addresses.

Fixes # (issue)

---

## Type of Change

- [ ] **Bug fix** (non-breaking fix for an issue)
- [ ] **New feature** (adds new functionality or robot behavior)
- [ ] **Protocol improvement** (V2V/V2I message structure or timing)
- [ ] **Simulation update** (Gazebo models, lighting, road network)
- [ ] **Dashboard / Telemetry update** (terminal UI or metrics)
- [ ] **Documentation update** (README, architecture diagrams)

---

## Testing & Verification

Describe testing performed to validate the changes:

- [ ] Workspace builds cleanly with `colcon build --symlink-install`
- [ ] Multi-robot simulation launched without errors (`multi_robot_v2x.launch.py`)
- [ ] Traffic light negotiation verified (`robot1` stops on red, crosses on green)
- [ ] Emergency corridor clearance verified (`ambulance` preempts civilian traffic)
- [ ] Parking spot allocation and parking maneuver tested (`robot2`)
- [ ] Telemetry dashboard renders without exceptions (`perception_dashboard`)

---

## Checklist

- [ ] My code adheres to PEP 8 standards.
- [ ] I have commented complex coordination logic.
- [ ] Documentation has been updated accordingly.
- [ ] No temporary files, build caches, or logs are included.
