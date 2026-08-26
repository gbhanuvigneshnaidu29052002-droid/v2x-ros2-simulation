#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TrafficLightController(Node):
    def __init__(self):
        super().__init__('traffic_light_controller')
        self.pub = self.create_publisher(String, '/v2x/traffic_light_state', 10)

        # Demo-friendly but still realistic timed traffic-light cycle.
        # First red lets everyone stop. Second red is longer so emergency behaviour is visible.
        self.initial_schedule = [
            ('GREEN', 8),
            ('YELLOW', 2),
            ('RED', 8),
            ('GREEN', 6),
            ('YELLOW', 2),
            ('RED', 14),
        ]

        self.normal_cycle = [
            ('GREEN', 12),
            ('YELLOW', 2),
            ('RED', 8),
        ]

        self.phase_source = 'initial'
        self.index = 0
        self.remaining = self.initial_schedule[0][1]
        self.current_state = self.initial_schedule[0][0]

        self.timer = self.create_timer(1.0, self.loop)
        self.get_logger().info('Traffic-light controller started.')
        self.get_logger().info('Cycle includes long RED phases for clear V2X demonstration.')

    def active_schedule(self):
        return self.initial_schedule if self.phase_source == 'initial' else self.normal_cycle

    def loop(self):
        msg = String()
        msg.data = self.current_state
        self.pub.publish(msg)

        self.get_logger().info(
            f'Traffic light: {self.current_state} | remaining={self.remaining}s | mode={self.phase_source}'
        )

        self.remaining -= 1

        if self.remaining <= 0:
            schedule = self.active_schedule()
            self.index += 1

            if self.phase_source == 'initial' and self.index >= len(self.initial_schedule):
                self.phase_source = 'normal'
                self.index = 0
                schedule = self.normal_cycle
            elif self.index >= len(schedule):
                self.index = 0

            schedule = self.active_schedule()
            self.current_state, self.remaining = schedule[self.index]


def main(args=None):
    rclpy.init(args=args)
    node = TrafficLightController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
