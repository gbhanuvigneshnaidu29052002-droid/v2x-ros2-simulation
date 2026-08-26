#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from nav_msgs.msg import Odometry


class ParkingManager(Node):
    def __init__(self):
        super().__init__('parking_manager')

        self.status_pub = self.create_publisher(String, '/v2x/parking_status', 10)
        self.assignment_pub = self.create_publisher(String, '/v2x/parking_assignment', 10)

        self.create_subscription(Bool, '/v2x/emergency_active', self.emergency_cb, 10)
        self.create_subscription(String, '/v2x/parking_feedback', self.feedback_cb, 10)

        for robot in ['robot1', 'robot2', 'robot3', 'ambulance']:
            self.create_subscription(
                Odometry,
                f'/{robot}/odom',
                lambda msg, r=robot: self.odom_cb(r, msg),
                10
            )

        # Vacancy-based predefined slots.
        # Add more normal slots here later, e.g. 'O3': 'FREE', and the next arriving robot can get it.
        self.normal_slots = ['O1', 'O2']
        self.hospital_slot = 'H1'

        self.slots = {
            'O1': 'FREE',
            'O2': 'FREE',
            'H1': 'FREE',
        }

        self.robot_x = {}
        self.robot_y = {}

        self.emergency_active = False
        self.assignments = {}
        self.no_slot_decisions = set()
        self.last_assignment = 'NONE'
        self.last_feedback = 'NONE'

        self.parking_trigger_x = 0.8

        self.timer = self.create_timer(1.0, self.loop)
        self.get_logger().info('Vacancy-based parking manager started.')
        self.get_logger().info('Normal slots: O1, O2. Ambulance slot: H1.')

    def odom_cb(self, robot, msg):
        self.robot_x[robot] = msg.pose.pose.position.x
        self.robot_y[robot] = msg.pose.pose.position.y

    def emergency_cb(self, msg):
        self.emergency_active = msg.data

    def feedback_cb(self, msg):
        self.last_feedback = msg.data
        parts = msg.data.strip().split(':')

        if len(parts) != 3:
            return

        robot, slot, state = parts
        if state != 'ARRIVED':
            return
        if slot not in self.slots:
            return

        if self.slots[slot] != f'OCCUPIED_BY_{robot}':
            self.slots[slot] = f'OCCUPIED_BY_{robot}'
            self.get_logger().warn(f'{robot} arrived at {slot}. Slot is now OCCUPIED.')

    def free_slot(self, slot_names):
        for slot in slot_names:
            if self.slots.get(slot) == 'FREE':
                return slot
        return None

    def assign(self, robot, slot):
        if robot in self.assignments:
            return

        if self.slots.get(slot) != 'FREE':
            return

        self.assignments[robot] = slot
        self.slots[slot] = f'RESERVED_FOR_{robot}'
        self.last_assignment = f'{robot}:{slot}'

        self.get_logger().warn(f'Assigned {robot} to free slot {slot}')

    def publish_assignment(self, robot, slot):
        msg = String()
        msg.data = f'{robot}:{slot}'
        self.assignment_pub.publish(msg)

    def publish_no_slot(self, robot):
        msg = String()
        msg.data = f'{robot}:NO_SLOT'
        self.assignment_pub.publish(msg)
        self.last_assignment = msg.data

    def loop(self):
        # 1. Normal robots request parking only when they approach the parking region.
        for robot in ['robot1', 'robot2', 'robot3']:
            x = self.robot_x.get(robot)

            if x is None:
                continue

            if robot in self.assignments or robot in self.no_slot_decisions:
                continue

            if x >= self.parking_trigger_x:
                slot = self.free_slot(self.normal_slots)

                if slot is not None:
                    self.assign(robot, slot)
                else:
                    self.no_slot_decisions.add(robot)
                    self.get_logger().warn(f'No normal parking slot free for {robot}. Robot will continue forward.')
                    self.publish_no_slot(robot)

        # 2. Ambulance only gets hospital bay H1.
        ambulance_x = self.robot_x.get('ambulance')
        if self.emergency_active and ambulance_x is not None:
            if 'ambulance' not in self.assignments and self.slots[self.hospital_slot] == 'FREE':
                self.assign('ambulance', self.hospital_slot)

        # 3. Re-publish current assignments so robots do not miss a single message.
        for robot, slot in self.assignments.items():
            if self.slots.get(slot) != f'OCCUPIED_BY_{robot}':
                self.publish_assignment(robot, slot)

        for robot in self.no_slot_decisions:
            if robot not in self.assignments:
                self.publish_no_slot(robot)

        status = (
            f'O1={self.slots["O1"]}; '
            f'O2={self.slots["O2"]}; '
            f'H1={self.slots["H1"]}; '
            f'assignments={self.assignments}; '
            f'no_slot={sorted(list(self.no_slot_decisions))}; '
            f'last_assignment={self.last_assignment}; '
            f'last_feedback={self.last_feedback}'
        )

        msg = String()
        msg.data = status
        self.status_pub.publish(msg)

        self.get_logger().info(f'Parking status: {status}')


def main(args=None):
    rclpy.init(args=args)
    node = ParkingManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
