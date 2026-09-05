# Security Policy

## Supported Versions

Security patches and vulnerability updates are provided for the following releases:

| Version / Branch | ROS 2 Distribution | Gazebo Version | Status |
| :--- | :--- | :--- | :--- |
| `main` | ROS 2 Humble Hawksbill | Gazebo 11 (Classic) | :white_check_mark: |
| Older releases | ROS 1 / Galactic / Foxy | Any | :x: |

---

## Reporting a Vulnerability

V2X communication and multi-robot fleet networks involve critical safety constraints. If you discover a potential vulnerability—such as message spoofing on broadcast topics (`/v2x/emergency_active`), denial-of-service in intersection controllers, or unbounded velocity injection—please notify us responsibly.

### Reporting Procedure

1. **GitHub Private Vulnerability Advisory (Recommended)**:
   - Go to the repository's **Security** tab.
   - Click **Report a vulnerability** to submit a confidential report.
2. **Direct Contact**:
   - Contact the project maintainer via GitHub: [@gbhanuvigneshnaidu29052002-droid](https://github.com/gbhanuvigneshnaidu29052002-droid).

### What to Include

- Detailed summary of the vulnerability and attack vector.
- Step-by-step instructions or proof-of-concept (PoC) code to reproduce.
- Potential impact on physical robot fleets and simulated infrastructure.

### Response Commitment

- We will acknowledge receipt within 48 hours.
- We will coordinate a remediation release and give public attribution upon patch publication (unless anonymity is requested).

Please refrain from submitting public issues for unresolved security concerns.
