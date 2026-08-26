#!/usr/bin/env python3

from pathlib import Path
import csv
import time

import rclpy
from rclpy.node import Node

from std_msgs.msg import String, Bool
from geometry_msgs.msg import Twist


class MetricsLogger(Node):
    def __init__(self):
        super().__init__('metrics_logger')

        self.start_time = time.time()

        self.traffic_light_state = 'UNKNOWN'
        self.emergency_active = False
        self.parking_status = 'UNKNOWN'
        self.parking_assignment = 'NONE'
        self.parking_feedback = 'NONE'

        self.robot1_speed = 0.0
        self.robot2_speed = 0.0
        self.ambulance_speed = 0.0

        self.csv_path = Path.home() / 'v2x_task5_ws' / 'v2x_metrics.csv'

        self.csv_file = open(self.csv_path, mode='w', newline='')
        self.writer = csv.writer(self.csv_file)

        self.writer.writerow([
            'time_s',
            'traffic_light_state',
            'emergency_active',
            'parking_status',
            'parking_assignment',
            'parking_feedback',
            'robot1_linear_x',
            'robot2_linear_x',
            'ambulance_linear_x'
        ])

        self.create_subscription(
            String,
            '/v2x/traffic_light_state',
            self.traffic_callback,
            10
        )

        self.create_subscription(
            Bool,
            '/v2x/emergency_active',
            self.emergency_callback,
            10
        )

        self.create_subscription(
            String,
            '/v2x/parking_status',
            self.parking_status_callback,
            10
        )

        self.create_subscription(
            String,
            '/v2x/parking_assignment',
            self.parking_assignment_callback,
            10
        )

        self.create_subscription(
            String,
            '/v2x/parking_feedback',
            self.parking_feedback_callback,
            10
        )

        self.create_subscription(
            Twist,
            '/robot1/cmd_vel',
            self.robot1_cmd_callback,
            10
        )

        self.create_subscription(
            Twist,
            '/robot2/cmd_vel',
            self.robot2_cmd_callback,
            10
        )

        self.create_subscription(
            Twist,
            '/ambulance/cmd_vel',
            self.ambulance_cmd_callback,
            10
        )

        self.timer = self.create_timer(1.0, self.write_row)

        self.get_logger().info(f'Metrics Logger started. Writing to: {self.csv_path}')

    def traffic_callback(self, msg):
        self.traffic_light_state = msg.data

    def emergency_callback(self, msg):
        self.emergency_active = msg.data

    def parking_status_callback(self, msg):
        self.parking_status = msg.data

    def parking_assignment_callback(self, msg):
        self.parking_assignment = msg.data

    def parking_feedback_callback(self, msg):
        self.parking_feedback = msg.data

    def robot1_cmd_callback(self, msg):
        self.robot1_speed = msg.linear.x

    def robot2_cmd_callback(self, msg):
        self.robot2_speed = msg.linear.x

    def ambulance_cmd_callback(self, msg):
        self.ambulance_speed = msg.linear.x

    def write_row(self):
        elapsed = round(time.time() - self.start_time, 2)

        self.writer.writerow([
            elapsed,
            self.traffic_light_state,
            self.emergency_active,
            self.parking_status,
            self.parking_assignment,
            self.parking_feedback,
            self.robot1_speed,
            self.robot2_speed,
            self.ambulance_speed
        ])

        self.csv_file.flush()

        self.get_logger().info(
            f't={elapsed}s | light={self.traffic_light_state} | '
            f'emergency={self.emergency_active} | '
            f'r1={self.robot1_speed:.2f} | '
            f'r2={self.robot2_speed:.2f} | '
            f'amb={self.ambulance_speed:.2f} | '
            f'parking={self.parking_status}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = MetricsLogger()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.csv_file.close()
    node.destroy_node()

    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
