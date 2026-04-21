from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='rfid',
            executable='secondary_auth_node',
            name='secondary_auth_node',
            output='screen',
        )
    ])