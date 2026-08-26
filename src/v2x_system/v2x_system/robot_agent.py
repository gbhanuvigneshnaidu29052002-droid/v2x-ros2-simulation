#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


def normalize_angle(angle):
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


def clamp(value, low, high):
    return max(low, min(high, value))


class RobotAgent(Node):
    def __init__(self):
        super().__init__('robot_agent')

        self.declare_parameter('robot_name', 'robot1')
        self.declare_parameter('cmd_vel_topic', '/cmd_vel')
        self.declare_parameter('odom_topic', '/odom')
        self.declare_parameter('is_emergency_vehicle', False)
        self.declare_parameter('enable_parking_behavior', True)

        self.robot_name = self.get_parameter('robot_name').value
        self.cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        self.odom_topic = self.get_parameter('odom_topic').value
        self.is_emergency_vehicle = bool(self.get_parameter('is_emergency_vehicle').value)
        self.enable_parking_behavior = bool(self.get_parameter('enable_parking_behavior').value)
        self.is_robot3 = self.robot_name == 'robot3'

        self.traffic_light_state = 'GREEN'
        self.emergency_active = False

        self.odom_received = False
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.stop_line_x = -2.2
        self.stop_zone_start_x = -2.85
        self.clear_intersection_x = -1.55
        self.visibility_range = 8.0
        self.has_cleared_light = False

        self.lane_y = {
            'robot1': -1.2,
            'robot2': 0.0,
            'robot3': 1.2,
            'ambulance': 1.2,
        }.get(self.robot_name, 0.0)

        self.robot3_cleared_lane = False
        self.robot3_yield_target_set = False
        self.robot3_target_x = -5.8
        self.robot3_target_y = 0.55

        self.parking_slot = None
        self.parking_phase = 'NO_DECISION'
        self.waypoint_index = 0
        self.last_feedback_ns = 0
        self.feedback_once = False

        self.paths = {
            'O1': [
                (-1.3, -1.2),
                (1.5, -1.2),
                (3.8, -1.2),
                (4.7, -2.8),
                (4.9, -4.0),
            ],
            'O2': [
                (-1.3, 0.0),
                (1.6, 0.0),
                (4.2, 0.0),
                (5.6, -2.8),
                (6.7, -4.0),
            ],
            'H1': [
                (-1.2, 1.2),
                (1.6, 1.2),
                (4.2, 1.2),
                (5.3, 2.6),
                (5.8, 4.0),
            ],
        }

        self.cmd_pub = self.create_publisher(Twist, self.cmd_vel_topic, 10)
        self.feedback_pub = self.create_publisher(String, '/v2x/parking_feedback', 10)
        self.perception_pub = self.create_publisher(String, f'/{self.robot_name}/traffic_light_perception', 10)

        self.create_subscription(String, '/v2x/traffic_light_state', self.traffic_cb, 10)
        self.create_subscription(Bool, '/v2x/emergency_active', self.emergency_cb, 10)
        self.create_subscription(String, '/v2x/parking_assignment', self.assignment_cb, 10)
        self.create_subscription(Odometry, self.odom_topic, self.odom_cb, 10)

        self.create_timer(0.1, self.control_loop)
        self.create_timer(0.5, self.publish_perception)

        self.get_logger().info(
            f'{self.robot_name} started | emergency_vehicle={self.is_emergency_vehicle} | '
            f'cmd={self.cmd_vel_topic} | odom={self.odom_topic}'
        )

    def traffic_cb(self, msg):
        self.traffic_light_state = msg.data

    def emergency_cb(self, msg):
        self.emergency_active = msg.data

    def odom_cb(self, msg):
        self.odom_received = True
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        self.yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        )

        if not self.has_cleared_light and self.x > self.clear_intersection_x:
            self.has_cleared_light = True
            self.get_logger().warn(f'{self.robot_name} crossed stop-line zone. Future red signals are ignored.')


    def choose_start_waypoint_index(self, slot):
        """
        Select the best waypoint to start from after receiving a parking assignment.
        This prevents the robot from turning back toward waypoints it already passed.
        """
        if slot not in self.paths or not self.odom_received:
            return 0

        path = self.paths[slot]

        best_index = 0
        best_score = 999999.0

        for i, (wx, wy) in enumerate(path):
            dx = wx - self.x
            dy = wy - self.y
            dist = math.hypot(dx, dy)

            # Strongly penalize waypoints far behind the robot.
            # The robots mainly travel from negative x to positive x.
            if wx < self.x - 0.6:
                dist += 100.0

            if dist < best_score:
                best_score = dist
                best_index = i

        return best_index


    def assignment_cb(self, msg):
        parts = msg.data.strip().split(':')
        if len(parts) != 2:
            return

        robot, decision = parts
        if robot != self.robot_name:
            return

        if decision == 'NO_SLOT':
            if self.parking_phase == 'NO_DECISION':
                self.parking_phase = 'NO_SLOT_CONTINUE'
                self.get_logger().warn(f'{self.robot_name} received NO_SLOT from parking manager. Continuing forward.')
            return

        if decision not in self.paths:
            return

        if self.parking_slot == decision:
            return

        if self.parking_slot is not None:
            return

        self.parking_slot = decision
        self.parking_phase = 'NAVIGATING_TO_SLOT'
        self.waypoint_index = self.choose_start_waypoint_index(decision)
        self.feedback_once = False
        self.get_logger().warn(
            f'{self.robot_name} accepted parking assignment: {decision}. '
            f'Starting from waypoint index {self.waypoint_index}.'
        )

    def publish_cmd(self, vx, wz=0.0):
        msg = Twist()
        msg.linear.x = float(vx)
        msg.angular.z = float(wz)
        self.cmd_pub.publish(msg)

    def in_main_lane(self):
        return -1.8 <= self.y <= 1.8

    def facing_east(self):
        return abs(normalize_angle(self.yaw)) < 1.2

    def signal_applies(self):
        if not self.odom_received:
            return False

        # Ambulance ignores traffic signal only when emergency is active.
        if self.is_emergency_vehicle and self.emergency_active:
            return False

        if self.has_cleared_light:
            return False

        if not self.in_main_lane():
            return False

        if not self.facing_east():
            return False

        distance = self.stop_line_x - self.x

        if distance < -0.15:
            return False

        if distance > self.visibility_range:
            return False

        return True

    def traffic_speed_cap(self):
        if not self.signal_applies():
            return None

        if self.traffic_light_state == 'RED':
            if self.x < self.stop_zone_start_x:
                return 0.07
            if self.x <= self.stop_line_x + 0.10:
                return 0.0
            return None

        if self.traffic_light_state == 'YELLOW':
            return 0.05

        return None

    def goto_target(self, tx, ty, max_speed):
        if not self.odom_received:
            self.publish_cmd(0.0, 0.0)
            return False

        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)

        if dist < 0.32:
            self.publish_cmd(0.0, 0.0)
            return True

        target_yaw = math.atan2(dy, dx)
        yaw_error = normalize_angle(target_yaw - self.yaw)

        wz = clamp(1.6 * yaw_error, -0.85, 0.85)

        if abs(yaw_error) > 0.75:
            vx = 0.0
        else:
            vx = min(max_speed, max(0.05, 0.55 * dist))

        cap = self.traffic_speed_cap()
        if cap is not None:
            vx = min(vx, cap)
            if cap == 0.0:
                wz = 0.0

        self.publish_cmd(vx, wz)
        return False

    def publish_arrival_feedback(self):
        now = self.get_clock().now().nanoseconds
        if now - self.last_feedback_ns < 1_000_000_000:
            return

        self.last_feedback_ns = now
        msg = String()
        msg.data = f'{self.robot_name}:{self.parking_slot}:ARRIVED'
        self.feedback_pub.publish(msg)

        if not self.feedback_once:
            self.feedback_once = True
            self.get_logger().warn(f'{self.robot_name} arrived at {self.parking_slot}. Feedback sent.')

    def navigate_to_parking(self):
        if self.parking_phase == 'PARKED':
            self.publish_cmd(0.0, 0.0)
            self.publish_arrival_feedback()
            return

        path = self.paths[self.parking_slot]

        if self.waypoint_index >= len(path):
            self.parking_phase = 'PARKED'
            self.publish_cmd(0.0, 0.0)
            self.publish_arrival_feedback()
            return

        tx, ty = path[self.waypoint_index]
        reached = self.goto_target(tx, ty, 0.22 if self.is_emergency_vehicle else 0.16)

        if reached:
            self.get_logger().info(
                f'{self.robot_name} reached waypoint {self.waypoint_index + 1}/{len(path)} for {self.parking_slot}'
            )
            self.waypoint_index += 1

    def robot3_behavior(self):
        # robot3 is a normal robot, but clears ambulance lane during emergency.
        if self.emergency_active and not self.robot3_cleared_lane:
            if not self.robot3_yield_target_set:
                self.robot3_target_x = max(self.x + 0.8, -5.9)
                self.robot3_target_y = 0.55
                self.robot3_yield_target_set = True

            reached = self.goto_target(self.robot3_target_x, self.robot3_target_y, 0.13)

            if reached or self.y < 0.75:
                self.robot3_cleared_lane = True
                self.lane_y = 0.55
                self.get_logger().warn('robot3 moved into queue lane behind front robots and cleared ambulance lane.')
            return

        # Continue forward like a normal vehicle and obey traffic rules.
        self.goto_target(self.x + 1.0, self.lane_y, 0.13)

    def normal_forward_behavior(self):
        self.goto_target(self.x + 1.0, self.lane_y, 0.15)

    def ambulance_behavior_without_assignment(self):
        # Before emergency, ambulance behaves like a normal vehicle.
        # During emergency, it ignores traffic light and moves faster.
        speed = 0.22 if self.emergency_active else 0.16
        self.goto_target(self.x + 1.0, 1.2, speed)

    def control_loop(self):
        if not self.odom_received:
            self.publish_cmd(0.0, 0.0)
            return

        if self.parking_slot is not None and self.enable_parking_behavior:
            self.navigate_to_parking()
            return

        if self.is_robot3:
            self.robot3_behavior()
            return

        if self.is_emergency_vehicle:
            self.ambulance_behavior_without_assignment()
            return

        self.normal_forward_behavior()

    def publish_perception(self):
        msg = String()

        cap = self.traffic_speed_cap()
        action = 'MOVE'
        if cap == 0.0:
            action = 'STOP_AT_RED_BEFORE_STOP_LINE'
        elif cap is not None and cap > 0.0:
            action = 'SLOW_FOR_SIGNAL'

        if not self.odom_received:
            msg.data = 'NO_ODOMETRY'
        elif self.is_emergency_vehicle and self.emergency_active:
            msg.data = (
                f'AMBULANCE_PRIORITY | ignores_light={self.traffic_light_state} | '
                f'action=MOVE_TO_HOSPITAL | parking={self.parking_slot or "WAITING_H1"} | '
                f'x={self.x:.2f} y={self.y:.2f}'
            )
        elif self.is_robot3 and self.emergency_active and not self.robot3_cleared_lane:
            msg.data = (
                f'ROBOT3_CLEARING_AMBULANCE_LANE | light={self.traffic_light_state} | '
                f'action=MERGE_TO_QUEUE_LANE | x={self.x:.2f} y={self.y:.2f}'
            )
        elif self.has_cleared_light:
            msg.data = (
                f'PASSED_STOP_LINE_IGNORE_LATER_RED | light={self.traffic_light_state} | '
                f'action={action} | parking={self.parking_slot or self.parking_phase} | '
                f'x={self.x:.2f} y={self.y:.2f}'
            )
        elif self.signal_applies():
            msg.data = (
                f'VISIBLE_AND_FACING | light={self.traffic_light_state} | '
                f'distance_to_stop_line={self.stop_line_x - self.x:.2f} | action={action} | '
                f'parking={self.parking_slot or self.parking_phase}'
            )
        else:
            msg.data = (
                f'LIGHT_NOT_RELEVANT | light={self.traffic_light_state} | action={action} | '
                f'parking={self.parking_slot or self.parking_phase} | x={self.x:.2f} y={self.y:.2f}'
            )

        self.perception_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = RobotAgent()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
