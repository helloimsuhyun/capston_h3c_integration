from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_path = get_package_share_directory('patrol_yolo')

    default_config = os.path.join(
        pkg_path,
        'config',
        'person_tracker.yaml'
    )

    mode = LaunchConfiguration('mode')
    config = LaunchConfiguration('config')

    server_ip = LaunchConfiguration('server_ip')
    server_url = ['http://', server_ip, ':8000/person_event']

    yolo_host = LaunchConfiguration('yolo_host')
    yolo_port = LaunchConfiguration('yolo_port')
    audio_host = LaunchConfiguration('audio_host')
    audio_port = LaunchConfiguration('audio_port')

    return LaunchDescription([
        DeclareLaunchArgument(
            'mode',
            default_value='realsense'
        ),

        DeclareLaunchArgument(
            'config',
            default_value=default_config
        ),

        DeclareLaunchArgument(
            'server_ip',
            default_value='192.168.0.16',
            description='A single IP address to construct all server URLs.'
        ),

        DeclareLaunchArgument('yolo_host', default_value='0.0.0.0'),
        DeclareLaunchArgument('yolo_port', default_value='8091'),

        DeclareLaunchArgument('audio_host', default_value='0.0.0.0'),
        DeclareLaunchArgument('audio_port', default_value='8092'),

        Node(
            package='patrol_yolo',
            executable='person_tracker_node',
            name='person_tracker_node',
            output='screen',
            parameters=[
                config,
                {'mode': mode},
            ],
        ),

        Node(
            package='patrol_yolo',
            executable='person_detect_control_node',
            name='person_detect_control_node',
            output='screen',
            parameters=[
                
                    config,
                    {
                    'robot_pose_topic': '/robot_pose',
                    'enable_topic': '/person_tracking/enable',
                    'notify_host': yolo_host,
                    'notify_port': yolo_port,
                    'log_region_match': True,
                    }
            ],
        ),
        Node(
            package='patrol_yolo',
            executable='audio_upload_control_node',
            name='audio_upload_control_node',
            output='screen',
            parameters=[
                {
                    'robot_pose_topic': '/robot_pose',
                    'upload_enable_topic': '/sound/upload_enable',
                    'allowed_labels_topic': '/sound/allowed_labels',
                    'notify_host': audio_host,
                    'notify_port': audio_port,
                    'log_region_match': True,
                    'start_enabled': True,
                }
            ],
        ),

        Node(
            package='patrol_yolo',
            executable='person_event_sender_node',
            name='person_event_sender_node',
            output='screen',
            parameters=[
                {
                    'tracks_topic': '/person_tracking/tracks_json',
                    'annotated_topic': '/person_tracking/annotated',
                    'robot_pose_topic': '/robot_pose',
                    'server_url': server_url,
                }
            ],
        ),

        Node(
            package='patrol_yolo',
            executable='person_following_node',
            name='person_following_node',
            output='screen',
            parameters=[
                config,
                {
                    'tracks_topic':  '/person_tracking/tracks_json',
                    'enable_topic':  '/person_tracking/enable',
                    'target_topic':  '/person_tracking/follow_target',
                    'state_topic':   '/person_tracking/follow_state',
                }
            ],
        ),
    ])


