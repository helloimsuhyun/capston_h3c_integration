**** 참고 https://rainbow-chaser.tistory.com/4


  1 package had stderr output: realsense2_ros_mqtt_bridge
chan@ubuntu:~/capston_h3c_integration$ source install/setup.bash 
chan@ubuntu:~/capston_h3c_integration$ ros2 launch capston_bringup bringup_all.launch.py 
[INFO] [launch]: All log files can be found below /home/chan/.ros/log/2026-04-16-21-44-28-670132-ubuntu-12800
[INFO] [launch]: Default logging verbosity is set to INFO
Warning: Parameter 'server_ip' is not supported. Supported parameters are:
['accel_fps', 'accelerate_gpu_with_glsl', 'align_depth.enable', 'angular_velocity_cov', 'base_frame_id', 'camera_name', 'camera_namespace', 'clip_distance', 'colorizer.enable', 'config_file', 'decimation_filter.enable', 'decimation_filter.filter_magnitude', 'depth_mapping_camera.labeled_point_cloud_profile', 'depth_mapping_camera.occupancy_profile', 'depth_module.color_format', 'depth_module.color_profile', 'depth_module.depth_format', 'depth_module.depth_profile', 'depth_module.enable_auto_exposure', 'depth_module.exposure', 'depth_module.exposure.1', 'depth_module.exposure.2', 'depth_module.gain', 'depth_module.gain.1', 'depth_module.gain.2', 'depth_module.hdr_enabled', 'depth_module.infra1_format', 'depth_module.infra2_format', 'depth_module.infra_format', 'depth_module.infra_profile', 'depth_module.inter_cam_sync_mode', 'device_type', 'diagnostics_period', 'disparity_filter.enable', 'enable_accel', 'enable_color', 'enable_depth', 'enable_gyro', 'enable_infra', 'enable_infra1', 'enable_infra2', 'enable_labeled_point_cloud', 'enable_motion', 'enable_occupancy', 'enable_rgbd', 'enable_safety', 'enable_sync', 'gyro_fps', 'hdr_merge.enable', 'hole_filling_filter.enable', 'initial_reset', 'json_file_path', 'linear_accel_cov', 'log_level', 'motion_fps', 'output', 'pointcloud.allow_no_texture_points', 'pointcloud.enable', 'pointcloud.ordered_pc', 'pointcloud.stream_filter', 'pointcloud.stream_index_filter', 'publish_tf', 'reconnect_timeout', 'rgb_camera.color_format', 'rgb_camera.color_profile', 'rgb_camera.enable_auto_exposure', 'rosbag_filename', 'rosbag_loop', 'rotation_filter.enable', 'rotation_filter.rotation', 'safety_camera.safety_mode', 'serial_no', 'spatial_filter.enable', 'temporal_filter.enable', 'tf_prefix', 'tf_publish_rate', 'unite_imu_method', 'usb_port_id', 'wait_for_device_timeout']
Warning: Parameter 'image_topic' is not supported. Supported parameters are:
['accel_fps', 'accelerate_gpu_with_glsl', 'align_depth.enable', 'angular_velocity_cov', 'base_frame_id', 'camera_name', 'camera_namespace', 'clip_distance', 'colorizer.enable', 'config_file', 'decimation_filter.enable', 'decimation_filter.filter_magnitude', 'depth_mapping_camera.labeled_point_cloud_profile', 'depth_mapping_camera.occupancy_profile', 'depth_module.color_format', 'depth_module.color_profile', 'depth_module.depth_format', 'depth_module.depth_profile', 'depth_module.enable_auto_exposure', 'depth_module.exposure', 'depth_module.exposure.1', 'depth_module.exposure.2', 'depth_module.gain', 'depth_module.gain.1', 'depth_module.gain.2', 'depth_module.hdr_enabled', 'depth_module.infra1_format', 'depth_module.infra2_format', 'depth_module.infra_format', 'depth_module.infra_profile', 'depth_module.inter_cam_sync_mode', 'device_type', 'diagnostics_period', 'disparity_filter.enable', 'enable_accel', 'enable_color', 'enable_depth', 'enable_gyro', 'enable_infra', 'enable_infra1', 'enable_infra2', 'enable_labeled_point_cloud', 'enable_motion', 'enable_occupancy', 'enable_rgbd', 'enable_safety', 'enable_sync', 'gyro_fps', 'hdr_merge.enable', 'hole_filling_filter.enable', 'initial_reset', 'json_file_path', 'linear_accel_cov', 'log_level', 'motion_fps', 'output', 'pointcloud.allow_no_texture_points', 'pointcloud.enable', 'pointcloud.ordered_pc', 'pointcloud.stream_filter', 'pointcloud.stream_index_filter', 'publish_tf', 'reconnect_timeout', 'rgb_camera.color_format', 'rgb_camera.color_profile', 'rgb_camera.enable_auto_exposure', 'rosbag_filename', 'rosbag_loop', 'rotation_filter.enable', 'rotation_filter.rotation', 'safety_camera.safety_mode', 'serial_no', 'spatial_filter.enable', 'temporal_filter.enable', 'tf_prefix', 'tf_publish_rate', 'unite_imu_method', 'usb_port_id', 'wait_for_device_timeout']
Warning: Parameter 'yolo_mode' is not supported. Supported parameters are:
['accel_fps', 'accelerate_gpu_with_glsl', 'align_depth.enable', 'angular_velocity_cov', 'base_frame_id', 'camera_name', 'camera_namespace', 'clip_distance', 'colorizer.enable', 'config_file', 'decimation_filter.enable', 'decimation_filter.filter_magnitude', 'depth_mapping_camera.labeled_point_cloud_profile', 'depth_mapping_camera.occupancy_profile', 'depth_module.color_format', 'depth_module.color_profile', 'depth_module.depth_format', 'depth_module.depth_profile', 'depth_module.enable_auto_exposure', 'depth_module.exposure', 'depth_module.exposure.1', 'depth_module.exposure.2', 'depth_module.gain', 'depth_module.gain.1', 'depth_module.gain.2', 'depth_module.hdr_enabled', 'depth_module.infra1_format', 'depth_module.infra2_format', 'depth_module.infra_format', 'depth_module.infra_profile', 'depth_module.inter_cam_sync_mode', 'device_type', 'diagnostics_period', 'disparity_filter.enable', 'enable_accel', 'enable_color', 'enable_depth', 'enable_gyro', 'enable_infra', 'enable_infra1', 'enable_infra2', 'enable_labeled_point_cloud', 'enable_motion', 'enable_occupancy', 'enable_rgbd', 'enable_safety', 'enable_sync', 'gyro_fps', 'hdr_merge.enable', 'hole_filling_filter.enable', 'initial_reset', 'json_file_path', 'linear_accel_cov', 'log_level', 'motion_fps', 'output', 'pointcloud.allow_no_texture_points', 'pointcloud.enable', 'pointcloud.ordered_pc', 'pointcloud.stream_filter', 'pointcloud.stream_index_filter', 'publish_tf', 'reconnect_timeout', 'rgb_camera.color_format', 'rgb_camera.color_profile', 'rgb_camera.enable_auto_exposure', 'rosbag_filename', 'rosbag_loop', 'rotation_filter.enable', 'rotation_filter.rotation', 'safety_camera.safety_mode', 'serial_no', 'spatial_filter.enable', 'temporal_filter.enable', 'tf_prefix', 'tf_publish_rate', 'unite_imu_method', 'usb_port_id', 'wait_for_device_timeout']
Warning: Parameter 'rgb_camera.enable_auto_white_balance' is not supported. Supported parameters are:
['accel_fps', 'accelerate_gpu_with_glsl', 'align_depth.enable', 'angular_velocity_cov', 'base_frame_id', 'camera_name', 'camera_namespace', 'clip_distance', 'colorizer.enable', 'config_file', 'decimation_filter.enable', 'decimation_filter.filter_magnitude', 'depth_mapping_camera.labeled_point_cloud_profile', 'depth_mapping_camera.occupancy_profile', 'depth_module.color_format', 'depth_module.color_profile', 'depth_module.depth_format', 'depth_module.depth_profile', 'depth_module.enable_auto_exposure', 'depth_module.exposure', 'depth_module.exposure.1', 'depth_module.exposure.2', 'depth_module.gain', 'depth_module.gain.1', 'depth_module.gain.2', 'depth_module.hdr_enabled', 'depth_module.infra1_format', 'depth_module.infra2_format', 'depth_module.infra_format', 'depth_module.infra_profile', 'depth_module.inter_cam_sync_mode', 'device_type', 'diagnostics_period', 'disparity_filter.enable', 'enable_accel', 'enable_color', 'enable_depth', 'enable_gyro', 'enable_infra', 'enable_infra1', 'enable_infra2', 'enable_labeled_point_cloud', 'enable_motion', 'enable_occupancy', 'enable_rgbd', 'enable_safety', 'enable_sync', 'gyro_fps', 'hdr_merge.enable', 'hole_filling_filter.enable', 'initial_reset', 'json_file_path', 'linear_accel_cov', 'log_level', 'motion_fps', 'output', 'pointcloud.allow_no_texture_points', 'pointcloud.enable', 'pointcloud.ordered_pc', 'pointcloud.stream_filter', 'pointcloud.stream_index_filter', 'publish_tf', 'reconnect_timeout', 'rgb_camera.color_format', 'rgb_camera.color_profile', 'rgb_camera.enable_auto_exposure', 'rosbag_filename', 'rosbag_loop', 'rotation_filter.enable', 'rotation_filter.rotation', 'safety_camera.safety_mode', 'serial_no', 'spatial_filter.enable', 'temporal_filter.enable', 'tf_prefix', 'tf_publish_rate', 'unite_imu_method', 'usb_port_id', 'wait_for_device_timeout']
Warning: Parameter 'rgb_camera.white_balance' is not supported. Supported parameters are:
['accel_fps', 'accelerate_gpu_with_glsl', 'align_depth.enable', 'angular_velocity_cov', 'base_frame_id', 'camera_name', 'camera_namespace', 'clip_distance', 'colorizer.enable', 'config_file', 'decimation_filter.enable', 'decimation_filter.filter_magnitude', 'depth_mapping_camera.labeled_point_cloud_profile', 'depth_mapping_camera.occupancy_profile', 'depth_module.color_format', 'depth_module.color_profile', 'depth_module.depth_format', 'depth_module.depth_profile', 'depth_module.enable_auto_exposure', 'depth_module.exposure', 'depth_module.exposure.1', 'depth_module.exposure.2', 'depth_module.gain', 'depth_module.gain.1', 'depth_module.gain.2', 'depth_module.hdr_enabled', 'depth_module.infra1_format', 'depth_module.infra2_format', 'depth_module.infra_format', 'depth_module.infra_profile', 'depth_module.inter_cam_sync_mode', 'device_type', 'diagnostics_period', 'disparity_filter.enable', 'enable_accel', 'enable_color', 'enable_depth', 'enable_gyro', 'enable_infra', 'enable_infra1', 'enable_infra2', 'enable_labeled_point_cloud', 'enable_motion', 'enable_occupancy', 'enable_rgbd', 'enable_safety', 'enable_sync', 'gyro_fps', 'hdr_merge.enable', 'hole_filling_filter.enable', 'initial_reset', 'json_file_path', 'linear_accel_cov', 'log_level', 'motion_fps', 'output', 'pointcloud.allow_no_texture_points', 'pointcloud.enable', 'pointcloud.ordered_pc', 'pointcloud.stream_filter', 'pointcloud.stream_index_filter', 'publish_tf', 'reconnect_timeout', 'rgb_camera.color_format', 'rgb_camera.color_profile', 'rgb_camera.enable_auto_exposure', 'rosbag_filename', 'rosbag_loop', 'rotation_filter.enable', 'rotation_filter.rotation', 'safety_camera.safety_mode', 'serial_no', 'spatial_filter.enable', 'temporal_filter.enable', 'tf_prefix', 'tf_publish_rate', 'unite_imu_method', 'usb_port_id', 'wait_for_device_timeout']
[INFO] [launch.user]: 🚀 Launching as Normal ROS Node
[INFO] [realsense2_camera_node-1]: process started with pid [12807]
[INFO] [capture_sender-2]: process started with pid [12809]
[INFO] [patrol_http_bridge-3]: process started with pid [12811]
[INFO] [person_tracker_node-4]: process started with pid [12813]
[INFO] [person_detect_control_node-5]: process started with pid [12815]
[INFO] [person_event_sender_node-6]: process started with pid [12817]
[INFO] [robot_pose_sender-7]: process started with pid [12819]
[INFO] [robot_goal_sender-8]: process started with pid [12823]
[INFO] [can_teacher_node-9]: process started with pid [12825]
[INFO] [patrol_command_bridge-10]: process started with pid [12827]
[INFO] [audio_frontend_node-11]: process started with pid [12829]
[INFO] [respeaker_doa_node-12]: process started with pid [12831]
[INFO] [yamnet_classifier_node-13]: process started with pid [12847]
[INFO] [sound_event_manager_node-14]: process started with pid [12856]
[INFO] [clip_transfer_node-15]: process started with pid [12858]
[INFO] [sound_event_monitor_node-16]: process started with pid [12867]
[realsense2_camera_node-1] [INFO] [1776343469.284563055] [camera.camera]: RealSense ROS v4.57.7
[realsense2_camera_node-1] [INFO] [1776343469.284851450] [camera.camera]: Built with LibRealSense v2.57.7
[realsense2_camera_node-1] [INFO] [1776343469.284890203] [camera.camera]: Running with LibRealSense v2.57.7
[sound_event_manager_node-14] [INFO] [1776343470.198652170] [sound_event_manager_node]: sound_event_manager_node started
[sound_event_monitor_node-16] [INFO] [1776343470.276707849] [sound_event_monitor_node]: sound_event_monitor_node started
[patrol_command_bridge-10] [INFO] [1776343470.559080929] [patrol_command_bridge]: PatrolCommandBridge started | server=http://192.168.0.221:8000 | waypoints_topic=/patrol/waypoints_json | command_topic=/patrol/command | reload_waypoints_topic=/patrol/reload_waypoints
[respeaker_doa_node-12] Traceback (most recent call last):
[respeaker_doa_node-12]   File "/home/chan/capston_h3c_integration/install/security_audio_frontend/lib/security_audio_frontend/respeaker_doa_node", line 33, in <module>
[respeaker_doa_node-12]     sys.exit(load_entry_point('security-audio-frontend==0.0.1', 'console_scripts', 'respeaker_doa_node')())
[respeaker_doa_node-12]   File "/home/chan/capston_h3c_integration/install/security_audio_frontend/lib/python3.10/site-packages/security_audio_frontend/respeaker_doa_node.py", line 91, in main
[respeaker_doa_node-12]     node = RespeakerDoaNode()
[respeaker_doa_node-12]   File "/home/chan/capston_h3c_integration/install/security_audio_frontend/lib/python3.10/site-packages/security_audio_frontend/respeaker_doa_node.py", line 39, in __init__
[respeaker_doa_node-12]     raise RuntimeError('ReSpeaker control device not found (0x2886:0x0018)')
[respeaker_doa_node-12] RuntimeError: ReSpeaker control device not found (0x2886:0x0018)
[robot_goal_sender-8] [INFO] [1776343470.618896753] [robot_goal_sender]: RobotGoalSender started | goal_topic=/goal_pose_2d | next_place_topic=/next_place_id | endpoint=http://192.168.0.221:8000/robot/goal
[realsense2_camera_node-1] [INFO] [1776343470.683654523] [camera.camera]: Device with serial number 241122307367 was found.
[realsense2_camera_node-1] 
[realsense2_camera_node-1] [INFO] [1776343470.685913648] [camera.camera]: Device with physical ID 2-1.2.4.3-5 was found.
[realsense2_camera_node-1] [INFO] [1776343470.686128632] [camera.camera]: Device with name Intel RealSense D455 was found.
[realsense2_camera_node-1] [INFO] [1776343470.686536135] [camera.camera]: Device with port number 2-1.2.4.3 was found.
[realsense2_camera_node-1] [INFO] [1776343470.686600394] [camera.camera]: Device USB type: 3.2
[realsense2_camera_node-1] [INFO] [1776343470.686790161] [camera.camera]: getParameters...
[realsense2_camera_node-1] [INFO] [1776343470.687226305] [camera.camera]: JSON file is not provided
[realsense2_camera_node-1] [INFO] [1776343470.687570926] [camera.camera]: Device Name: Intel RealSense D455
[realsense2_camera_node-1] [INFO] [1776343470.688291529] [camera.camera]: Device Serial No: 241122307367
[realsense2_camera_node-1] [INFO] [1776343470.688344683] [camera.camera]: Device physical port: 2-1.2.4.3-5
[realsense2_camera_node-1] [INFO] [1776343470.688380589] [camera.camera]: Device FW version: 5.17.0.10
[realsense2_camera_node-1] [INFO] [1776343470.688654487] [camera.camera]: Device Product ID: 0x0B5C
[realsense2_camera_node-1] [INFO] [1776343470.688694105] [camera.camera]: Sync Mode: Off
[clip_transfer_node-15] [INFO] [1776343470.743305476] [clip_transfer_node]: clip_transfer_node started | server_url=http://192.168.0.221:8000 | pose_topic=/robot_pose
[robot_pose_sender-7] [INFO] [1776343470.868529686] [robot_pose_sender]: RobotPoseSender started | topic=/robot_pose | status_topic=/robot_status | endpoint=http://192.168.0.221:8000/robot/pose
[ERROR] [respeaker_doa_node-12]: process has died [pid 12831, exit code 1, cmd '/home/chan/capston_h3c_integration/install/security_audio_frontend/lib/security_audio_frontend/respeaker_doa_node --ros-args -r __node:=respeaker_doa_node --params-file /home/chan/capston_h3c_integration/install/security_audio_frontend/share/security_audio_frontend/config/frontend.yaml'].
[can_teacher_node-9] [INFO] [1776343471.033909392] [can_teacher_node]: CAN bus connected: can0
[can_teacher_node-9] [ERROR] [1776343471.038275764] [can_teacher_node]: CAN loop error: Error receiving: Network is down [Error Code 100]
[can_teacher_node-9] [INFO] [1776343471.051205211] [can_teacher_node]: CanTeacherNode started | pose_topic=/robot_pose | server=http://192.168.0.221:8000 | can_if=can0 | teach_can_id=0x102
[audio_frontend_node-11] [INFO] [1776343471.053785660] [audio_frontend_node]: Using input device index=0, name="NVIDIA Jetson Orin NX HDA: HDMI 0 (hw:0,3)", input_channels=6, channel_index=0, sample_rate=16000
[audio_frontend_node-11] Expression 'parameters->channelCount <= maxChans' failed in 'src/hostapi/alsa/pa_linux_alsa.c', line: 1514
[audio_frontend_node-11] Expression 'ValidateParameters( inputParameters, hostApi, StreamDirection_In )' failed in 'src/hostapi/alsa/pa_linux_alsa.c', line: 2818
[audio_frontend_node-11] Traceback (most recent call last):
[audio_frontend_node-11]   File "/home/chan/capston_h3c_integration/install/security_audio_frontend/lib/security_audio_frontend/audio_frontend_node", line 33, in <module>
[audio_frontend_node-11]     sys.exit(load_entry_point('security-audio-frontend==0.0.1', 'console_scripts', 'audio_frontend_node')())
[audio_frontend_node-11]   File "/home/chan/capston_h3c_integration/install/security_audio_frontend/lib/python3.10/site-packages/security_audio_frontend/audio_frontend_node.py", line 258, in main
[audio_frontend_node-11]     node = AudioFrontendNode()
[audio_frontend_node-11]   File "/home/chan/capston_h3c_integration/install/security_audio_frontend/lib/python3.10/site-packages/security_audio_frontend/audio_frontend_node.py", line 96, in __init__
[audio_frontend_node-11]     self.start_audio_stream()
[audio_frontend_node-11]   File "/home/chan/capston_h3c_integration/install/security_audio_frontend/lib/python3.10/site-packages/security_audio_frontend/audio_frontend_node.py", line 129, in start_audio_stream
[audio_frontend_node-11]     self.stream = sd.InputStream(
[audio_frontend_node-11]   File "/home/chan/.local/lib/python3.10/site-packages/sounddevice.py", line 1457, in __init__
[audio_frontend_node-11]     _StreamBase.__init__(self, kind='input', wrap_callback='array',
[audio_frontend_node-11]   File "/home/chan/.local/lib/python3.10/site-packages/sounddevice.py", line 914, in __init__
[audio_frontend_node-11]     _check(_lib.Pa_OpenStream(self._ptr, iparameters, oparameters,
[audio_frontend_node-11]   File "/home/chan/.local/lib/python3.10/site-packages/sounddevice.py", line 2838, in _check
[audio_frontend_node-11]     raise PortAudioError(errormsg, err)
[audio_frontend_node-11] sounddevice.PortAudioError: Error opening InputStream: Invalid number of channels [PaErrorCode -9998]
[patrol_http_bridge-3] [INFO] [1776343471.414672938] [patrol_http_bridge]: HTTP bridge ready at :8090
[patrol_http_bridge-3] INFO:     Started server process [12811]
[patrol_http_bridge-3] INFO:     Waiting for application startup.
[patrol_http_bridge-3] INFO:     Application startup complete.
[patrol_http_bridge-3] INFO:     Uvicorn running on http://0.0.0.0:8090 (Press CTRL+C to quit)
[person_event_sender_node-6] [INFO] [1776343471.456303912] [person_event_sender_node]: [INIT] PersonEventSenderNode | tracks=/person_tracking/tracks_json | annotated=/person_tracking/annotated | robot_pose=/robot_pose
[ERROR] [audio_frontend_node-11]: process has died [pid 12829, exit code 1, cmd '/home/chan/capston_h3c_integration/install/security_audio_frontend/lib/security_audio_frontend/audio_frontend_node --ros-args -r __node:=audio_frontend_node --params-file /home/chan/capston_h3c_integration/install/security_audio_frontend/share/security_audio_frontend/config/frontend.yaml'].
[capture_sender-2] [INFO] [1776343471.576323341] [capture_sender]: server_url     = http://192.168.0.221:8000
[capture_sender-2] [INFO] [1776343471.576989158] [capture_sender]: signaling_url  = http://192.168.0.221:8001
[capture_sender-2] [INFO] [1776343471.577475705] [capture_sender]: n_frames       = 5
[capture_sender-2] [INFO] [1776343471.577956875] [capture_sender]: sample_dt      = 0.2
[capture_sender-2] [INFO] [1776343471.578441341] [capture_sender]: capture_timeout_s = 5.0
[capture_sender-2] [INFO] [1776343471.578898062] [capture_sender]: post_timeout_s    = 10.0
[capture_sender-2] [INFO] [1776343471.599966055] [capture_sender]: capture sender ready
[person_detect_control_node-5] /opt/ros/humble/local/lib/python3.10/dist-packages/rclpy/node.py:440: UserWarning: when declaring parameter named 'start_enabled', declaring a parameter only providing its name is deprecated. You have to either:
[person_detect_control_node-5]  - Pass a name and a default value different to "PARAMETER NOT SET" (and optionally a descriptor).
[person_detect_control_node-5]  - Pass a name and a parameter type.
[person_detect_control_node-5]  - Pass a name and a descriptor with `dynamic_typing=True
[person_detect_control_node-5]   warnings.warn(
[person_detect_control_node-5] INFO:     Started server process [12815]
[person_detect_control_node-5] INFO:     Waiting for application startup.
[person_detect_control_node-5] INFO:     Application startup complete.
[person_detect_control_node-5] INFO:     Uvicorn running on http://0.0.0.0:8091 (Press CTRL+C to quit)
[person_detect_control_node-5] [INFO] [1776343471.838586171] [person_detect_control_node]: [INIT] PersonDetectControlNode | robot_pose=/robot_pose | enable_topic=/person_tracking/enable | notify_http=0.0.0.0:8091 | startup_publish=disabled_until_first_config
[person_detect_control_node-5] [INFO] [1776343471.839529727] [person_detect_control_node]: [YOLO ENABLE] True reason=startup_mode_global
[person_detect_control_node-5] [INFO] [1776343471.840073075] [person_detect_control_node]: Initial state published: True
[patrol_command_bridge-10] [WARN] [1776343473.578807760] [patrol_command_bridge]: Timeout while fetching patrol waypoints
[person_tracker_node-4] [INFO] [1776343474.713784622] [person_tracker_node]: Loading YOLO model: /home/chan/capston_h3c_integration/src/patrol_yolo/model/yolov8n.engine
[person_tracker_node-4] [INFO] [1776343474.736576323] [person_tracker_node]: [MODE] realsense | color_topic=/camera/camera/color/image_raw | depth_topic=/camera/camera/aligned_depth_to_color/image_raw
[person_tracker_node-4] [INFO] [1776343474.739572307] [person_tracker_node]: [CONTROL] YOLO inference default=ON
[person_tracker_node-4] [INFO] [1776343474.740164457] [person_tracker_node]: PersonTrackerNode initialized with worker thread.
[patrol_command_bridge-10] [WARN] [1776343475.586467757] [patrol_command_bridge]: Timeout while fetching patrol command
[realsense2_camera_node-1] [WARN] [1776343475.928740633] [camera.camera]: re-enable the stream for the change to take effect.
[realsense2_camera_node-1] [INFO] [1776343475.934357387] [camera.camera]: Set ROS param depth_module.infra_profile to default: 848x480x30
[realsense2_camera_node-1] [WARN] [1776343476.649800693] [camera.camera]: re-enable the stream for the change to take effect.
[realsense2_camera_node-1] [INFO] [1776343476.651110630] [camera.camera]: Set ROS param gyro_fps to default: 200
[realsense2_camera_node-1] [INFO] [1776343476.651232459] [camera.camera]: Set ROS param accel_fps to default: 100
[realsense2_camera_node-1] [INFO] [1776343476.678478786] [camera.camera]: Stopping Sensor: Depth Module
[realsense2_camera_node-1] [INFO] [1776343476.678820527] [camera.camera]: Stopping Sensor: RGB Camera
[realsense2_camera_node-1] [INFO] [1776343476.809923397] [camera.camera]: Starting Sensor: Depth Module
[realsense2_camera_node-1] [INFO] [1776343476.903578951] [camera.camera]: Open profile: stream_type: Depth(0), Format: Z16, Width: 640, Height: 480, FPS: 30
[realsense2_camera_node-1]  16/04 21:44:36,908 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:36,920 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:36,931 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:36,941 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:36,952 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:36,963 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:36,974 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:36,985 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:36,996 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,007 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1] [INFO] [1776343477.020933083] [camera.camera]: Starting Sensor: RGB Camera
[realsense2_camera_node-1] [INFO] [1776343477.043868816] [camera.camera]: Open profile: stream_type: Color(0), Format: RGB8, Width: 640, Height: 480, FPS: 30
[realsense2_camera_node-1] [INFO] [1776343477.086564772] [camera.camera]: RealSense Node Is Up!
[realsense2_camera_node-1]  16/04 21:44:37,323 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,334 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,346 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,357 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,369 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,482 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,493 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,504 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,515 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,525 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,536 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,547 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,558 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,569 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,580 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,591 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[patrol_command_bridge-10] [WARN] [1776343477.592104311] [patrol_command_bridge]: Timeout while fetching patrol command
[realsense2_camera_node-1]  16/04 21:44:37,602 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,612 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,623 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:37,634 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[person_tracker_node-4] /usr/lib/python3/dist-packages/scipy/__init__.py:146: UserWarning: A NumPy version >=1.17.3 and <1.25.0 is required for this version of SciPy (detected version 1.26.4
[person_tracker_node-4]   warnings.warn(f"A NumPy version >={np_minversion} and <{np_maxversion}"
[person_tracker_node-4] Loading /home/chan/capston_h3c_integration/src/patrol_yolo/model/yolov8n.engine for TensorRT inference...
[person_tracker_node-4] [04/16/2026-21:44:38] [TRT] [I] Loaded engine size: 13 MiB
[person_tracker_node-4] [04/16/2026-21:44:38] [TRT] [W] Using an engine plan file across different models of devices is not recommended and is likely to affect performance or even cause errors.
[person_tracker_node-4] [04/16/2026-21:44:38] [TRT] [I] [MemUsageChange] TensorRT-managed allocation in IExecutionContext creation: CPU +0, GPU +18, now: CPU 0, GPU 30 (MiB)
[patrol_command_bridge-10] [WARN] [1776343479.599325336] [patrol_command_bridge]: Timeout while fetching patrol command
[yamnet_classifier_node-13] [INFO] [1776343480.302471941] [yamnet_classifier_node]: worker ready: {"ready": true, "load_model_sec": 5.440779685974121, "gpus": []}
[yamnet_classifier_node-13] [INFO] [1776343480.303206624] [yamnet_classifier_node]: yamnet_classifier_node started
[patrol_command_bridge-10] [WARN] [1776343481.606978439] [patrol_command_bridge]: Timeout while fetching patrol command
[patrol_command_bridge-10] [WARN] [1776343483.613624145] [patrol_command_bridge]: Timeout while fetching patrol command
[patrol_command_bridge-10] [WARN] [1776343485.619829869] [patrol_command_bridge]: Timeout while fetching patrol command
[patrol_command_bridge-10] [WARN] [1776343487.628372420] [patrol_command_bridge]: Timeout while fetching patrol command
[patrol_command_bridge-10] [WARN] [1776343489.638036778] [patrol_command_bridge]: Timeout while fetching patrol command
[patrol_command_bridge-10] [WARN] [1776343491.647477584] [patrol_command_bridge]: Timeout while fetching patrol command
[patrol_command_bridge-10] [WARN] [1776343493.658820678] [patrol_command_bridge]: Timeout while fetching patrol command
[realsense2_camera_node-1]  16/04 21:44:54,947 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:54,958 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[realsense2_camera_node-1]  16/04 21:44:54,969 WARNING [281472392751328] (messenger-libusb.cpp:42) control_transfer returned error, index: 768, error: Resource temporarily unavailable, number: 11
[patrol_command_bridge-10] [WARN] [1776343495.666799759] [patrol_command_bridge]: Timeout while fetching patrol command
[patrol_command_bridge-10] [WARN] [1776343497.675533410] [patrol_command_bridge]: Timeout while fetching patrol command
[patrol_command_bridge-10] [WARN] [1776343499.684691222] [patrol_command_bridge]: Timeout while fetching patrol command
[patrol_command_bridge-10] [WARN] [1776343501.694049957] [patrol_command_bridge]: Timeout while fetching patrol command
[patrol_command_bridge-10] [WARN] [1776343503.704492687] [patrol_command_bridge]: Timeout while fetching patrol command
[patrol_command_bridge-10] [WARN] [1776343505.712713698] [patrol_command_bridge]: Timeout while fetching patrol command
[patrol_command_bridge-10] [WARN] [1776343507.721292155] [patrol_command_bridge]: Timeout while fetching patrol command
[patrol_command_bridge-10] [WARN] [1776343509.728980529] [patrol_command_bridge]: Timeout while fetching patrol command
[patrol_command_bridge-10] [WARN] [1776343511.737018065] [patrol_command_bridge]: Timeout while fetching patrol command
[person_event_sender_node-6] [WARN] [1776343512.303808889] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343513.732855529] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[patrol_command_bridge-10] [WARN] [1776343513.748793299] [patrol_command_bridge]: Timeout while fetching patrol command
[person_event_sender_node-6] [WARN] [1776343513.825703588] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343513.863709805] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343513.943672136] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343514.007591445] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343514.078956737] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343514.157702221] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343514.229212350] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343514.292961410] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343514.361960924] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343514.423512435] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343514.474928875] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343514.543036294] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343514.628274643] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343514.703105495] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343514.763979959] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343514.835701359] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343514.906769297] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343514.975848205] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343515.047379548] [person_event_sender_node]: [SEND] skipped (person_present): no robot pose cached
[person_event_sender_node-6] [WARN] [1776343515.116360369] [person_event_sender_node]: [SEND] skipped (person_present): no rob

0. 
제트팩 버전 확인  ==============================================
dpkg-query --show nvidia-l4t-core
apt show nvidia-jetpack

>>jP 6.2 계열로 확인


파이썬, 넘파이 , 제트팩 버전 확인  ==============================================

python3 --version
python3 -c "import sys; import numpy; print(sys.version); print(numpy.__version__)"
uname -m
>>
JetPack Runtime 6.2.1
Python 3.10.12
aarch64

설치 ==============================================
sudo apt-get update
sudo apt-get install -y python3-pip libopenblas-dev

pip3 install numpy==1.26.4
pip3 uninstall torch torchvision ultralytics -y

wget https://raw.githubusercontent.com/pytorch/pytorch/5c6af2b583709f6176898c017424dc9981023c28/.ci/docker/common/install_cusparselt.sh
sudo CUDA_VERSION=12.6 bash ./install_cusparselt.sh

* 다운받은 wget이 cuda version 적용 및 문법 오류가 있을 수  있는데 gpt 시켜서 ./install_cusparselt.sh를 수정해야한다.

========= 
1. torch
wget https://developer.download.nvidia.com/compute/redist/jp/v61/pytorch/torch-2.5.0a0+872d972e41.nv24.08.17622132-cp310-cp310-linux_aarch64.whl
python3 -m pip install --no-cache ./torch-2.5.0a0+872d972e41.nv24.08.17622132-cp310-cp310-linux_aarch64.whl

python3 - <<EOF
import torch
print(torch.__version__)
print(torch.cuda.is_available())
EOF


2. torchvision

sudo apt-get install -y libjpeg-dev zlib1g-dev libpng-dev git

git clone --branch v0.20.0 https://github.com/pytorch/vision.git
cd vision

python3 -m pip install -v --no-build-isolation .
cd ..

확인 ========================================== 
python3 - <<EOF
import torch
print(torch.__version__)
print(torch.cuda.is_available())
print(torch.version.cuda)
if torch.cuda.is_available():
    print(torch.cuda.get_device_name(0))
EOF

python3 -m pip install -U ultralytics

확인 ===
python3 - <<EOF
from ultralytics import YOLO
print("ultralytics ok")
EOF


0.1 pt파일 텐서화 

- python3 export_engine.py --model yolov8n.pt --half
# 추론 이미지 사이즈 640, FP16 최적화 >> engine 파일 생성

- yaml 설정에서 model path를 engine파일의 절대경로로 변경




==================================

1. 
cd ~/ros2_ws
colcon build --packages-select person_tracker_ros
source install/setup.bash

ros2 launch patrol_yolo person_tracker.launch.py


==============================


2. 확인 및 I/O정리

트레킹 결과 토픽 -- /person_tracking/tracks_json
ros2 topic echo /person_tracking/tracks_json


트레킹 시각화 토픽 -- /person_tracking/annotated
rqt_image_view





python3 -c "import sys, torch; print(sys.executable); print(torch.__version__); print(torch.cuda.is_available())"

colcon build --packages-select person_tracker_ros
source install/setup.bash
ros2 launch person_tracker_ros person_tracker.launch.py