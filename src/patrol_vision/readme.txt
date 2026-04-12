

chan@ubuntu:~/capston_h3c_integration$ ros2 launch capston_bringup bringup_all.launch.py 
[INFO] [launch]: All log files can be found below /home/chan/.ros/log/2026-04-12-17-56-33-552248-ubuntu-19743
[INFO] [launch]: Default logging verbosity is set to INFO
[INFO] [capture_sender-1]: process started with pid [19752]
[INFO] [camera_publisher-2]: process started with pid [19754]
[INFO] [patrol_http_bridge-3]: process started with pid [19756]
[INFO] [robot_pose_sender-4]: process started with pid [19758]
[INFO] [robot_goal_sender-5]: process started with pid [19760]
[INFO] [can_teacher_node-6]: process started with pid [19762]
[INFO] [patrol_command_bridge-7]: process started with pid [19764]
[INFO] [audio_frontend_node-8]: process started with pid [19766]
[INFO] [respeaker_doa_node-9]: process started with pid [19768]
[INFO] [yamnet_classifier_node-10]: process started with pid [19784]
[INFO] [sound_event_manager_node-11]: process started with pid [19786]
[INFO] [clip_transfer_node-12]: process started with pid [19788]
[INFO] [sound_event_monitor_node-13]: process started with pid [19790]
[INFO] [person_tracker_node-14]: process started with pid [19793]
[INFO] [person_detect_control_node-15]: process started with pid [19796]
[INFO] [person_event_sender_node-16]: process started with pid [19799]
[patrol_command_bridge-7] [INFO] [1775984194.998175481] [patrol_command_bridge]: PatrolCommandBridge started | server=http://192.168.0.16:8000 | waypoints_topic=/patrol/waypoints_json | command_topic=/patrol/command | reload_waypoints_topic=/patrol/reload_waypoints
[sound_event_manager_node-11] [INFO] [1775984195.036812451] [sound_event_manager_node]: sound_event_manager_node started
[patrol_command_bridge-7] [INFO] [1775984195.116235644] [patrol_command_bridge]: Published patrol waypoints | n=3
[sound_event_monitor_node-13] [INFO] [1775984195.244240707] [sound_event_monitor_node]: sound_event_monitor_node started
[respeaker_doa_node-9] [INFO] [1775984195.617188752] [respeaker_doa_node]: respeaker_doa_node started
[patrol_command_bridge-7] [INFO] [1775984195.907389720] [patrol_command_bridge]: Published patrol command | command=idle
[audio_frontend_node-8] [INFO] [1775984196.069634074] [audio_frontend_node]: Using input device index=0, name="ReSpeaker 4 Mic Array (UAC1.0): USB Audio (hw:0,0)", input_channels=6, channel_index=0, sample_rate=16000
[audio_frontend_node-8] Expression 'parameters->channelCount <= maxChans' failed in 'src/hostapi/alsa/pa_linux_alsa.c', line: 1514
[audio_frontend_node-8] Expression 'ValidateParameters( inputParameters, hostApi, StreamDirection_In )' failed in 'src/hostapi/alsa/pa_linux_alsa.c', line: 2818
[audio_frontend_node-8] Traceback (most recent call last):
[audio_frontend_node-8]   File "/home/chan/capston_h3c_integration/install/security_audio_frontend/lib/security_audio_frontend/audio_frontend_node", line 33, in <module>
[audio_frontend_node-8]     sys.exit(load_entry_point('security-audio-frontend==0.0.1', 'console_scripts', 'audio_frontend_node')())
[audio_frontend_node-8]   File "/home/chan/capston_h3c_integration/install/security_audio_frontend/lib/python3.10/site-packages/security_audio_frontend/audio_frontend_node.py", line 258, in main
[audio_frontend_node-8]     node = AudioFrontendNode()
[audio_frontend_node-8]   File "/home/chan/capston_h3c_integration/install/security_audio_frontend/lib/python3.10/site-packages/security_audio_frontend/audio_frontend_node.py", line 96, in __init__
[audio_frontend_node-8]     self.start_audio_stream()
[audio_frontend_node-8]   File "/home/chan/capston_h3c_integration/install/security_audio_frontend/lib/python3.10/site-packages/security_audio_frontend/audio_frontend_node.py", line 129, in start_audio_stream
[audio_frontend_node-8]     self.stream = sd.InputStream(
[audio_frontend_node-8]   File "/home/chan/.local/lib/python3.10/site-packages/sounddevice.py", line 1457, in __init__
[audio_frontend_node-8]     _StreamBase.__init__(self, kind='input', wrap_callback='array',
[audio_frontend_node-8]   File "/home/chan/.local/lib/python3.10/site-packages/sounddevice.py", line 914, in __init__
[audio_frontend_node-8]     _check(_lib.Pa_OpenStream(self._ptr, iparameters, oparameters,
[audio_frontend_node-8]   File "/home/chan/.local/lib/python3.10/site-packages/sounddevice.py", line 2838, in _check
[audio_frontend_node-8]     raise PortAudioError(errormsg, err)
[audio_frontend_node-8] sounddevice.PortAudioError: Error opening InputStream: Invalid number of channels [PaErrorCode -9998]
[can_teacher_node-6] [INFO] [1775984196.287336427] [can_teacher_node]: CAN bus connected: can0
[camera_publisher-2] [INFO] [1775984196.289020545] [camera_publisher]: calib_file path : /home/chan/capston_h3c_integration/data/camera_intrinsics.yaml
[clip_transfer_node-12] [INFO] [1775984196.290467568] [clip_transfer_node]: clip_transfer_node started | server_url=http://192.168.0.16:8000 | pose_topic=/robot_pose
[can_teacher_node-6] [ERROR] [1775984196.315092370] [can_teacher_node]: CAN loop error: Error receiving: Network is down [Error Code 100]
[can_teacher_node-6] [INFO] [1775984196.316773001] [can_teacher_node]: CanTeacherNode started | pose_topic=/robot_pose | server=http://192.168.0.16:8000 | can_if=can0 | teach_can_id=0x102
[robot_goal_sender-5] [INFO] [1775984196.368151378] [robot_goal_sender]: RobotGoalSender started | goal_topic=/goal_pose_2d | next_place_topic=/next_place_id | endpoint=http://192.168.0.16:8000/robot/goal
[person_event_sender_node-16] [INFO] [1775984196.374979280] [person_event_sender_node]: [INIT] PersonEventSenderNode | tracks=/person_tracking/tracks_json | annotated=/person_tracking/annotated | robot_pose=/robot_pose
[robot_pose_sender-4] [INFO] [1775984196.394689586] [robot_pose_sender]: RobotPoseSender started | topic=/robot_pose | status_topic=/robot_status | endpoint=http://192.168.0.16:8000/robot/pose
[person_detect_control_node-15] /opt/ros/humble/local/lib/python3.10/dist-packages/rclpy/node.py:440: UserWarning: when declaring parameter named 'start_enabled', declaring a parameter only providing its name is deprecated. You have to either:
[person_detect_control_node-15]         - Pass a name and a default value different to "PARAMETER NOT SET" (and optionally a descriptor).
[person_detect_control_node-15]         - Pass a name and a parameter type.
[person_detect_control_node-15]         - Pass a name and a descriptor with `dynamic_typing=True
[person_detect_control_node-15]   warnings.warn(
[camera_publisher-2] [ WARN:0@2.028] global cap_v4l.cpp:982 open VIDEOIO(V4L2:/dev/video0): can't open camera by index
[camera_publisher-2] [ WARN:0@2.028] global cap.cpp:342 open VIDEOIO(V4L2): backend is generally available but can't be used to capture by index
[camera_publisher-2] [INFO] [1775984196.443349635] [camera_publisher]: ok: v4l2-ctl -d /dev/video0 --set-ctrl=auto_exposure=3
[camera_publisher-2] [INFO] [1775984196.492270652] [camera_publisher]: ok: v4l2-ctl -d /dev/video0 --set-ctrl=white_balance_automatic=0
[camera_publisher-2] [INFO] [1775984196.517855101] [camera_publisher]: ok: v4l2-ctl -d /dev/video0 --set-ctrl=white_balance_temperature=4500
[camera_publisher-2] [INFO] [1775984196.553596264] [camera_publisher]: ok: v4l2-ctl -d /dev/video0 --set-ctrl=focus_automatic_continuous=0
[camera_publisher-2] [INFO] [1775984196.554309696] [camera_publisher]: camera resolution: 0.0 x 0.0
[camera_publisher-2] [INFO] [1775984196.554867730] [camera_publisher]: camera fps: 0.0
[capture_sender-1] [INFO] [1775984196.561167519] [capture_sender]: server_url     = http://192.168.0.16:8000
[capture_sender-1] [INFO] [1775984196.561919063] [capture_sender]: signaling_url  = http://192.168.0.16:8001
[capture_sender-1] [INFO] [1775984196.562472521] [capture_sender]: n_frames       = 5
[capture_sender-1] [INFO] [1775984196.562984442] [capture_sender]: sample_dt      = 0.2
[capture_sender-1] [INFO] [1775984196.563496875] [capture_sender]: capture_timeout_s = 5.0
[capture_sender-1] [INFO] [1775984196.563998555] [capture_sender]: post_timeout_s    = 10.0
[camera_publisher-2] Traceback (most recent call last):
[camera_publisher-2]   File "/home/chan/capston_h3c_integration/install/patrol_vision/lib/patrol_vision/camera_publisher", line 33, in <module>
[camera_publisher-2]     sys.exit(load_entry_point('patrol-vision==0.0.0', 'console_scripts', 'camera_publisher')())
[camera_publisher-2]   File "/home/chan/capston_h3c_integration/install/patrol_vision/lib/python3.10/site-packages/patrol_vision/camera_publisher.py", line 164, in main
[camera_publisher-2]     node = CameraPublisher()
[camera_publisher-2]   File "/home/chan/capston_h3c_integration/install/patrol_vision/lib/python3.10/site-packages/patrol_vision/camera_publisher.py", line 136, in __init__
[camera_publisher-2]     raise RuntimeError("camera open failed")
[camera_publisher-2] RuntimeError: camera open failed
[person_detect_control_node-15] INFO:     Started server process [19796]
[person_detect_control_node-15] INFO:     Waiting for application startup.
[person_detect_control_node-15] INFO:     Application startup complete.
[person_detect_control_node-15] INFO:     Uvicorn running on http://0.0.0.0:8091 (Press CTRL+C to quit)
[person_detect_control_node-15] [INFO] [1775984196.701957191] [person_detect_control_node]: [INIT] PersonDetectControlNode | robot_pose=/robot_pose | enable_topic=/person_tracking/enable | notify_http=0.0.0.0:8091 | startup_publish=disabled_until_first_config
[person_detect_control_node-15] [INFO] [1775984196.704835941] [person_detect_control_node]: [YOLO ENABLE] True reason=startup_mode_global
[ERROR] [audio_frontend_node-8]: process has died [pid 19766, exit code 1, cmd '/home/chan/capston_h3c_integration/install/security_audio_frontend/lib/security_audio_frontend/audio_frontend_node --ros-args -r __node:=audio_frontend_node --params-file /home/chan/capston_h3c_integration/install/security_audio_frontend/share/security_audio_frontend/config/frontend.yaml'].
[person_detect_control_node-15] [INFO] [1775984196.706447769] [person_detect_control_node]: Initial state published: True
[capture_sender-1] [WebRTC] start() called
[capture_sender-1] [WebRTC] signaling_base_url = http://192.168.0.16:8001
[capture_sender-1] [WebRTC] image_topic = /camera/color/image_raw
[capture_sender-1] [WebRTC] size = 1280 x 720 fps = 30
[capture_sender-1] [WebRTC] bitrate = 4000000
[capture_sender-1] [WebRTC] use_hw_encoder = True
[capture_sender-1] [WebRTC] GLib loop started
[capture_sender-1] [WebRTC] creating GStreamer pipeline:
[capture_sender-1] appsrc name=src is-live=true block=false format=time do-timestamp=true caps=video/x-raw,format=BGR,width=1280,height=720,framerate=30/1 ! queue leaky=downstream max-size-buffers=1 ! videoconvert ! video/x-raw,format=I420 ! nvvidconv ! video/x-raw(memory:NVMM),format=NV12 ! nvv4l2h264enc bitrate=4000000 insert-sps-pps=true iframeinterval=30 idrinterval=30 control-rate=1 preset-level=1 maxperf-enable=1  ! h264parse config-interval=-1 ! rtph264pay pt=96 config-interval=1 ! application/x-rtp,media=video,encoding-name=H264,payload=96 ! webrtcbin name=webrtc bundle-policy=max-bundle stun-server=stun://stun.l.google.com:19302
[capture_sender-1] Traceback (most recent call last):
[capture_sender-1]   File "/home/chan/capston_h3c_integration/install/patrol_vision/lib/patrol_vision/capture_sender", line 33, in <module>
[capture_sender-1]     sys.exit(load_entry_point('patrol-vision==0.0.0', 'console_scripts', 'capture_sender')())
[capture_sender-1]   File "/home/chan/capston_h3c_integration/install/patrol_vision/lib/python3.10/site-packages/patrol_vision/capture_sender.py", line 192, in main
[capture_sender-1]     node = CaptureSender()
[capture_sender-1]   File "/home/chan/capston_h3c_integration/install/patrol_vision/lib/python3.10/site-packages/patrol_vision/capture_sender.py", line 82, in __init__
[capture_sender-1]     self.webrtc_sender.start()
[capture_sender-1]   File "/home/chan/capston_h3c_integration/install/patrol_vision/lib/python3.10/site-packages/patrol_vision/webrtc_sender.py", line 206, in start
[capture_sender-1]     self._build_pipeline()
[capture_sender-1]   File "/home/chan/capston_h3c_integration/install/patrol_vision/lib/python3.10/site-packages/patrol_vision/webrtc_sender.py", line 327, in _build_pipeline
[capture_sender-1]     self.pipeline = Gst.parse_launch(pipeline_str)
[capture_sender-1] gi.repository.GLib.GError: gst_parse_error: could not link rtph264pay0 to webrtc, webrtc can't handle caps application/x-rtp, media=(string)video, encoding-name=(string)H264, payload=(int)96 (3)
[ERROR] [capture_sender-1]: process has died [pid 19752, exit code 1, cmd '/home/chan/capston_h3c_integration/install/patrol_vision/lib/patrol_vision/capture_sender --ros-args -r __node:=capture_sender --params-file /tmp/launch_params_9uuoko_q'].
[ERROR] [camera_publisher-2]: process has died [pid 19754, exit code 1, cmd '/home/chan/capston_h3c_integration/install/patrol_vision/lib/patrol_vision/camera_publisher --ros-args -r __node:=camera_publisher --params-file /tmp/launch_params_9b6oj2fm -r /camera/color/image_raw:=/camera/color/image_raw'].
[patrol_http_bridge-3] [INFO] [1775984197.459388674] [patrol_http_bridge]: HTTP bridge ready at :8090
[patrol_http_bridge-3] INFO:     Started server process [19756]
[patrol_http_bridge-3] INFO:     Waiting for application startup.
[patrol_http_bridge-3] INFO:     Application startup complete.
[patrol_http_bridge-3] ERROR:    [Errno 98] error while attempting to bind on address ('0.0.0.0', 8090): address already in use
[patrol_http_bridge-3] INFO:     Waiting for application shutdown.
[patrol_http_bridge-3] INFO:     Application shutdown complete.
[person_tracker_node-14] [INFO] [1775984200.444548970] [person_tracker_node]: Loading YOLO model: /home/chan/capston_h3c_integration/src/patrol_yolo/model/yolov8n.engine
[person_tracker_node-14] [INFO] [1775984200.517269420] [person_tracker_node]: [MODE] webcam | color_topic=/camera/color/image_raw
[person_tracker_node-14] [INFO] [1775984200.519763453] [person_tracker_node]: [CONTROL] YOLO inference default=ON
[person_tracker_node-14] [INFO] [1775984200.520359313] [person_tracker_node]: PersonTrackerNode initialized with worker thread.
[yamnet_classifier_node-10] [INFO] [1775984204.914303482] [yamnet_classifier_node]: worker ready: {"ready": true, "load_model_sec": 5.172091484069824, "gpus": []}
[yamnet_classifier_node-10] [INFO] [1775984204.914975632] [yamnet_classifier_node]: yamnet_classifier_node started"""



1. 카메라 캘리브레이션

ros2 run patrol_vision camera_publisher

# patrol vison 파일 위에서 실행 저장경로 
ros2 run patrol_vision camera_calib_cli_node \
  --ros-args \
  -p cols:=6 \
  -p rows:=11 \
  -p square_size:=0.05 \
  -p marker_size:=0.037 \
  -p save_dir:=./data/calib_images \
  -p output_yaml:=./data/camera_intrinsics.yaml


  ros2 run patrol_vision camera_calib_cli_node --ros-args \
  -p cols:=11 \
  -p rows:=6 \
  -p square_size:=0.05 \
  -p image_topic:=/camera/color/image_raw \
  -p save_dir:=./data/calib_images