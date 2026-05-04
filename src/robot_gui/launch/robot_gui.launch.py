from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_path = get_package_share_directory('robot_gui')

    map_yaml_path = os.path.join(
        pkg_path,
        'maps',
        'map.yaml'
    )

    return LaunchDescription([
        Node(
            package='robot_gui',
            executable='robot_gui_node',
            name='robot_gui_node',
            output='screen',
            parameters=[
                {
                    'map_yaml_path': map_yaml_path,
                }
            ],
        )
    ])