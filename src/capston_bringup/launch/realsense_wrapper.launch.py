from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            namespace='camera',
            name='camera',
            output='screen',
            parameters=[{
                'rgb_camera.color_profile': '1280x720x30',
                'depth_module.depth_profile': '1280x720x30',
                'enable_depth': True,
                'enable_color': True,
                'align_depth.enable': True,
                'rgb_camera.enable_auto_exposure': True,
            }]
        )
    ])