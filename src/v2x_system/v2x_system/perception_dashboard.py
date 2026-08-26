#!/usr/bin/env python3
import os
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import Twist


class PerceptionDashboard(Node):
    def __init__(self):
        super().__init__('perception_dashboard')

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

        self.timer = self.create_timer(0.5, self.display)

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

    def display(self):
        os.system('clear')
        print('============================================================================')
        print('                    V2X SYSTEM DASHBOARD')
        print('============================================================================')
        print(f'Traffic Light     : {self.light}')
        print(f'Emergency Active  : {self.emergency}')
        print(f'Parking Manager   : {self.parking}')
        print(f'Last Assignment   : {self.assignment}')
        print(f'Last Feedback     : {self.feedback}')
        print('----------------------------------------------------------------------------')
        print('Robot       Speed     Perception / Decision')
        print('----------------------------------------------------------------------------')
        print(f'robot1      {self.speed["robot1"]:.2f}      {self.perception["robot1"]}')
        print(f'robot2      {self.speed["robot2"]:.2f}      {self.perception["robot2"]}')
        print(f'robot3      {self.speed["robot3"]:.2f}      {self.perception["robot3"]}')
        print(f'ambulance   {self.speed["ambulance"]:.2f}      {self.perception["ambulance"]}')
        print('----------------------------------------------------------------------------')
        print('Rules: normal robots stop before red stop line; after crossing, red is ignored.')
        print('Parking: vacancy-based O1/O2 allocation; ambulance only gets H1.')
        print('Emergency: robot3 clears ambulance lane; ambulance ignores red only in emergency.')
        print('============================================================================')


def main(args=None):
    rclpy.init(args=args)
    node = PerceptionDashboard()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
