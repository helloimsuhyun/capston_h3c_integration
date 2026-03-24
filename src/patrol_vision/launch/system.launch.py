from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    server_url = LaunchConfiguration('server_url')
    signaling_url = LaunchConfiguration('signaling_url')
    n_frames = LaunchConfiguration('n_frames')
    sample_dt = LaunchConfiguration('sample_dt')
    capture_timeout_s = LaunchConfiguration('capture_timeout_s')
    post_timeout_s = LaunchConfiguration('post_timeout_s')

    return LaunchDescription([
        DeclareLaunchArgument('server_url', default_value='http://192.168.0.221:8000'),
        DeclareLaunchArgument('signaling_url', default_value='http://192.168.0.221:8001'),
        DeclareLaunchArgument('n_frames', default_value='5'),
        DeclareLaunchArgument('sample_dt', default_value='0.2'),
        DeclareLaunchArgument('capture_timeout_s', default_value='5.0'),
        DeclareLaunchArgument('post_timeout_s', default_value='10.0'),

        Node(
            # 웹캠 카메라 publish node
            package="patrol_vision",
            executable="camera_publisher",
            name="camera_publisher",
            output="screen",
        ),

        Node(
            package="patrol_vision",
            executable="capture_sender",
            name="capture_sender",
            output="screen",
            parameters=[
                {
                    "server_url": server_url,
                    "signaling_url": signaling_url,
                    "n_frames": n_frames,
                    "sample_dt": sample_dt,
                    "capture_timeout_s": capture_timeout_s,
                    "post_timeout_s": post_timeout_s,
                }
            ],
        ),

        Node(
            package="patrol_vision",
            executable="patrol_http_bridge",
            name="patrol_http_bridge",
            output="screen",
        ),
    ])