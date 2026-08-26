from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'v2x_system'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ganeshna',
    maintainer_email='ganeshna@example.com',
    description='V2X traffic, emergency priority, and vacancy-based parking simulation',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'traffic_light_controller = v2x_system.traffic_light_controller:main',
            'emergency_manager = v2x_system.emergency_manager:main',
            'parking_manager = v2x_system.parking_manager:main',
            'metrics_logger = v2x_system.metrics_logger:main',
            'robot_agent = v2x_system.robot_agent:main',
            'perception_dashboard = v2x_system.perception_dashboard:main',
        ],
    },
)
