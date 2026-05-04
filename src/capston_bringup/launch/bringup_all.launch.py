from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, GroupAction, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    patrol_vision_dir = get_package_share_directory('patrol_vision')
    patrol_bridge_dir = get_package_share_directory('patrol_bridge')
    security_audio_system_dir = get_package_share_directory('security_audio_system')
    patrol_yolo_system_dir = get_package_share_directory('patrol_yolo')
    rfid_dir = get_package_share_directory('rfid')
    robot_gui_dir = get_package_share_directory('robot_gui')
    capston_bringup_dir = get_package_share_directory('capston_bringup')

    server_ip_arg = DeclareLaunchArgument(
        'server_ip',
        default_value='192.168.0.221',
        description='A single IP address to construct all server URLs.'
    )

    image_topic_arg = DeclareLaunchArgument(
        'image_topic',
        default_value='/camera/camera/color/image_raw',
        description='Image topic used by patrol vision nodes.'
    )

    yolo_mode_arg = DeclareLaunchArgument(
        'yolo_mode',
        default_value='realsense'
    )

    yolo_port_arg = DeclareLaunchArgument('yolo_port', default_value='8091')
    audio_port_arg = DeclareLaunchArgument('audio_port', default_value='8092')

    # GUI 실행 여부
    enable_gui_arg = DeclareLaunchArgument(
        'enable_gui',
        default_value='true',
        description='Whether to launch robot_gui.'
    )

    server_ip = LaunchConfiguration('server_ip')
    image_topic = LaunchConfiguration('image_topic')
    yolo_mode = LaunchConfiguration('yolo_mode')
    yolo_port = LaunchConfiguration('yolo_port')
    audio_port = LaunchConfiguration('audio_port')
    enable_gui = LaunchConfiguration('enable_gui')

    server_url = ['http://', server_ip, ':8000']
    signaling_url = ['http://', server_ip, ':8001']

    realsense_launch = GroupAction(
        scoped=True,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(capston_bringup_dir, 'launch', 'realsense_wrapper.launch.py')
                )
            )
        ]
    )

    vision_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(patrol_vision_dir, 'launch', 'system.launch.py')),
        launch_arguments={
            'server_url': server_url,
            'signaling_url': signaling_url,
            'image_topic': image_topic,
        }.items()
    )

    bridge_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(patrol_bridge_dir, 'launch', 'bringup.launch.py')),
        launch_arguments={
            'server_url': server_url,
        }.items()
    )

    audio_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(security_audio_system_dir, 'launch', 'bringup.launch.py')),
        launch_arguments={
            'server_url': server_url,
        }.items()
    )

    yolo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(patrol_yolo_system_dir, 'launch', 'person_tracker.launch.py')),
        launch_arguments={
            'server_ip': server_ip,
            'mode': yolo_mode,
            'yolo_port': yolo_port,
            'audio_port': audio_port,
        }.items()
    )

    rfid_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(rfid_dir, 'launch', 'rfid.launch.py')
        ),
        launch_arguments={
            'server_url': server_url,
        }.items()
    )

    robot_gui_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(robot_gui_dir, 'launch', 'robot_gui.launch.py')
        ),
        condition=IfCondition(enable_gui)
    )

    return LaunchDescription([
        server_ip_arg,
        image_topic_arg,
        yolo_mode_arg,
        yolo_port_arg,
        audio_port_arg,
        enable_gui_arg,

        realsense_launch,

        TimerAction(
            period=3.0,
            actions=[
                vision_launch,
                yolo_launch,
                bridge_launch,
                audio_launch,
                rfid_launch,
                robot_gui_launch,
            ]
        )
    ])