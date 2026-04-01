
1. 카메라 캘리브레이션

ros2 run patrol_vision camera_publisher

# patrol vison 파일 위에서 실행 저장경로 
ros2 run patrol_vision camera_calib_cli_node \
  --ros-args \
  -p cols:=11 \
  -p rows:=6 \
  -p square_size:=0.05 \
  -p marker_size:=0.037 \
  -p save_dir:=./data/calib_images \
  -p output_yaml:=./data/camera_intrinsics.yaml