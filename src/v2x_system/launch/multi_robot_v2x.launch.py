#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def spawn_turtlebot(name, x, y, yaw):
    tb3_dir = get_package_share_directory('turtlebot3_gazebo')
    burger_sdf = os.path.join(tb3_dir, 'models', 'turtlebot3_burger', 'model.sdf')

    return Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name=f'spawn_{name}',
        output='screen',
        arguments=[
            '-entity', name,
            '-file', burger_sdf,
            '-x', str(x),
            '-y', str(y),
            '-z', '0.05',
            '-Y', str(yaw),
            '-robot_namespace', f'/{name}',
        ]
    )


def robot_agent(name, emergency_vehicle):
    return Node(
        package='v2x_system',
        executable='robot_agent',
        name=f'{name}_agent',
        output='screen',
        parameters=[
            {'robot_name': name},
            {'cmd_vel_topic': f'/{name}/cmd_vel'},
            {'odom_topic': f'/{name}/odom'},
            {'is_emergency_vehicle': emergency_vehicle},
            {'enable_parking_behavior': True},
        ]
    )


def generate_launch_description():
    gazebo_ros_dir = get_package_share_directory('gazebo_ros')
    tb3_dir = get_package_share_directory('turtlebot3_gazebo')
    v2x_dir = get_package_share_directory('v2x_system')

    world = os.path.join(v2x_dir, 'worlds', 'v2x_city.world')

    tb3_models = os.path.join(tb3_dir, 'models')
    old_model_path = os.environ.get('GAZEBO_MODEL_PATH', '')
    model_path = tb3_models if not old_model_path else tb3_models + ':' + old_model_path

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_ros_dir, 'launch', 'gazebo.launch.py')),
        launch_arguments={'world': world}.items()
    )

    return LaunchDescription([
        SetEnvironmentVariable('GAZEBO_MODEL_PATH', model_path),

        gazebo,

        TimerAction(
            period=3.0,
            actions=[
                spawn_turtlebot('robot1', -5.4, -1.2, 0.0),
                spawn_turtlebot('robot2', -5.4, 0.0, 0.0),
                spawn_turtlebot('robot3', -7.2, 1.2, 0.0),
                spawn_turtlebot('ambulance', -10.8, 1.2, 0.0),
            ]
        ),

        TimerAction(
            period=8.0,
            actions=[
                Node(package='v2x_system', executable='traffic_light_controller', name='traffic_light_controller', output='screen'),
                Node(package='v2x_system', executable='emergency_manager', name='emergency_manager', output='screen'),
                Node(package='v2x_system', executable='parking_manager', name='parking_manager', output='screen'),
                Node(package='v2x_system', executable='metrics_logger', name='metrics_logger', output='screen'),
                robot_agent('robot1', False),
                robot_agent('robot2', False),
                robot_agent('robot3', False),
                robot_agent('ambulance', True),
            ]
        ),
    ])
