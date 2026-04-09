from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression
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

    # 상위 런치 제어값
    server_ip = LaunchConfiguration('server_ip')
    server_port = LaunchConfiguration('server_port')

    notify_host = LaunchConfiguration('notify_host')
    notify_port = LaunchConfiguration('notify_port')

    server_url = PythonExpression([
        '"http://"', server_ip, '":"', server_port, '"/person_event"'
    ])

    return LaunchDescription([
        DeclareLaunchArgument(
            'mode',
            default_value='webcam'
        ),

        DeclareLaunchArgument(
            'config',
            default_value=default_config
        ),

        # 이벤트 받을 서버 IP/PORT
        DeclareLaunchArgument(
            'server_ip',
            default_value='192.168.0.16'
        ),
        DeclareLaunchArgument(
            'server_port',
            default_value='8000'
        ),

        # robot/yolo_config 받을 로컬 HTTP 서버 바인딩
        DeclareLaunchArgument(
            'notify_host',
            default_value='0.0.0.0'
        ),
        DeclareLaunchArgument(
            'notify_port',
            default_value='8091'
        ),

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
                {
                    'robot_pose_topic': '/robot_pose',
                    'enable_topic': '/person_tracking/enable',
                    'notify_host': notify_host,
                    'notify_port': notify_port,
                    'start_enabled': False,
                    'fail_safe_disable': True,
                    'log_region_match': True,
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
    ])