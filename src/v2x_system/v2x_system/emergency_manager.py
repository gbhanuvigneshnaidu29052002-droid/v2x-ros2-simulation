#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from nav_msgs.msg import Odometry


class EmergencyManager(Node):
    def __init__(self):
        super().__init__('emergency_manager')
        self.pub = self.create_publisher(Bool, '/v2x/emergency_active', 10)
        self.create_subscription(Odometry, '/ambulance/odom', self.ambulance_odom_cb, 10)

        self.odom_received = False
        self.ambulance_x = -999.0
        self.last_state = None

        # Emergency activates when ambulance approaches the city/intersection.
        self.activation_x = -8.8
        self.deactivation_x = 6.1

        self.timer = self.create_timer(0.5, self.loop)
        self.get_logger().info('Emergency manager started.')
        self.get_logger().info('Emergency becomes active based on ambulance odometry, not manual switching.')

    def ambulance_odom_cb(self, msg):
        self.odom_received = True
        self.ambulance_x = msg.pose.pose.position.x

    def loop(self):
        active = False
        if self.odom_received:
            active = self.activation_x <= self.ambulance_x <= self.deactivation_x

        msg = Bool()
        msg.data = active
        self.pub.publish(msg)

        if active != self.last_state:
            self.last_state = active
            if active:
                self.get_logger().warn(
                    f'EMERGENCY ACTIVE: ambulance x={self.ambulance_x:.2f}. Normal robots obey traffic; ambulance has priority.'
                )
            else:
                self.get_logger().info('Emergency inactive.')


def main(args=None):
    rclpy.init(args=args)
    node = EmergencyManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
