#!/usr/bin/env python3

import csv
from pathlib import Path

import rclpy
from rclpy.node import Node

from std_msgs.msg import String, Bool
from geometry_msgs.msg import Twist


class EvidenceCollector(Node):
    def __init__(self):
        super().__init__('evidence_collector')

        self.base_dir = Path.home() / 'v2x_task5_ws/final_submission/evidence_auto'
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.csv_path = self.base_dir / 'v2x_live_evidence.csv'
        self.txt_path = self.base_dir / 'v2x_latest_snapshot.txt'

        self.light = 'WAITING'
        self.emergency = 'WAITING'
        self.parking = 'WAITING'
        self.assignment = 'WAITING'
        self.feedback = 'WAITING'

        self.perception = {
            'robot1': 'WAITING',
            'robot2': 'WAITING',
            'robot3': 'WAITING',
            'ambulance': 'WAITING',
        }

        self.speed = {
            'robot1': 0.0,
            'robot2': 0.0,
            'robot3': 0.0,
            'ambulance': 0.0,
        }

        self.create_subscription(String, '/v2x/traffic_light_state', self.light_cb, 10)
        self.create_subscription(Bool, '/v2x/emergency_active', self.emergency_cb, 10)
        self.create_subscription(String, '/v2x/parking_status', self.parking_cb, 10)
        self.create_subscription(String, '/v2x/parking_assignment', self.assignment_cb, 10)
        self.create_subscription(String, '/v2x/parking_feedback', self.feedback_cb, 10)

        for robot in ['robot1', 'robot2', 'robot3', 'ambulance']:
            self.create_subscription(
                String,
                f'/{robot}/traffic_light_perception',
                lambda msg, r=robot: self.perception_cb(r, msg),
                10
            )

            self.create_subscription(
                Twist,
                f'/{robot}/cmd_vel',
                lambda msg, r=robot: self.speed_cb(r, msg),
                10
            )

        if not self.csv_path.exists():
            with self.csv_path.open('w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'time_s',
                    'traffic_light',
                    'emergency_active',
                    'parking_status',
                    'last_assignment',
                    'last_feedback',
                    'robot1_speed',
                    'robot2_speed',
                    'robot3_speed',
                    'ambulance_speed',
                    'robot1_perception',
                    'robot2_perception',
                    'robot3_perception',
                    'ambulance_perception',
                ])

        self.start_time = self.get_clock().now().nanoseconds / 1e9
        self.timer = self.create_timer(1.0, self.log_snapshot)

        self.get_logger().info(f'Evidence collector started.')
        self.get_logger().info(f'CSV evidence: {self.csv_path}')
        self.get_logger().info(f'Latest snapshot: {self.txt_path}')

    def light_cb(self, msg):
        self.light = msg.data

    def emergency_cb(self, msg):
        self.emergency = str(msg.data)

    def parking_cb(self, msg):
        self.parking = msg.data

    def assignment_cb(self, msg):
        self.assignment = msg.data

    def feedback_cb(self, msg):
        self.feedback = msg.data

    def perception_cb(self, robot, msg):
        self.perception[robot] = msg.data

    def speed_cb(self, robot, msg):
        self.speed[robot] = msg.linear.x

    def log_snapshot(self):
        now = self.get_clock().now().nanoseconds / 1e9
        t = round(now - self.start_time, 2)

        row = [
            t,
            self.light,
            self.emergency,
            self.parking,
            self.assignment,
            self.feedback,
            round(self.speed['robot1'], 3),
            round(self.speed['robot2'], 3),
            round(self.speed['robot3'], 3),
            round(self.speed['ambulance'], 3),
            self.perception['robot1'],
            self.perception['robot2'],
            self.perception['robot3'],
            self.perception['ambulance'],
        ]

        with self.csv_path.open('a', newline='') as f:
            csv.writer(f).writerow(row)

        text = f"""============================================================
V2X LIVE EVIDENCE SNAPSHOT
============================================================
time_s              : {t}
traffic_light        : {self.light}
emergency_active     : {self.emergency}
parking_status       : {self.parking}
last_assignment      : {self.assignment}
last_feedback        : {self.feedback}

robot1 speed         : {self.speed['robot1']:.2f}
robot1 perception    : {self.perception['robot1']}

robot2 speed         : {self.speed['robot2']:.2f}
robot2 perception    : {self.perception['robot2']}

robot3 speed         : {self.speed['robot3']:.2f}
robot3 perception    : {self.perception['robot3']}

ambulance speed      : {self.speed['ambulance']:.2f}
ambulance perception : {self.perception['ambulance']}
============================================================
"""
        self.txt_path.write_text(text)


def main(args=None):
    rclpy.init(args=args)
    node = EvidenceCollector()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()

    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
