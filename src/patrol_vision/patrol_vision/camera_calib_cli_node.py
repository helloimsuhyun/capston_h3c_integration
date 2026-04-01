import os
import cv2
import time
import queue
import threading
import numpy as np
from pathlib import Path

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2.aruco as aruco

class CameraCalibCliNode(Node):
    def __init__(self):
        super().__init__("camera_calib_cli_node")

        # 1. 파라미터 선언 및 로드
        self.declare_parameter("image_topic", "/camera/color/image_raw")
        self.declare_parameter("save_dir", "./calib_images")
        self.declare_parameter("output_yaml", "./camera_intrinsics.yaml")
        self.declare_parameter("cols", 11)              
        self.declare_parameter("rows", 6)               
        self.declare_parameter("square_size", 0.05)     
        self.declare_parameter("marker_size", 0.037)    
        self.declare_parameter("preview", True)

        self.save_dir = str(self.get_parameter("save_dir").value)
        self.output_yaml = str(self.get_parameter("output_yaml").value)
        self.cols = int(self.get_parameter("cols").value)
        self.rows = int(self.get_parameter("rows").value)
        self.square_size = float(self.get_parameter("square_size").value)
        self.marker_size = float(self.get_parameter("marker_size").value)
        self.preview = bool(self.get_parameter("preview").value)

        # 2. Charuco 보드 및 Detector 설정 (순서 고정)
        self.dictionary = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
        self.board = aruco.CharucoBoard(
            (self.cols, self.rows), 
            self.square_size, 
            self.marker_size, 
            self.dictionary
        )

        self.params = aruco.DetectorParameters()
        self.params.adaptiveThreshWinSizeMin = 3
        self.params.adaptiveThreshWinSizeMax = 23
        self.params.adaptiveThreshWinSizeStep = 10
        self.params.minMarkerPerimeterRate = 0.03 

        # [수정] Detector는 여기서 한 번만 생성합니다.
        self.detector = aruco.CharucoDetector(self.board, detectorParams=self.params)

        # 터미널 로깅용 상태 변수
        self.last_found_status = False

        # 나머지 초기화
        Path(self.save_dir).mkdir(parents=True, exist_ok=True)
        self.debug_corners_dir = Path(self.save_dir) / "debug_corners"
        self.debug_corners_dir.mkdir(parents=True, exist_ok=True)

        self.bridge = CvBridge()
        self.latest_frame = None
        self.lock = threading.Lock()
        self.cmd_queue = queue.Queue()

        self.sub = self.create_subscription(Image, str(self.get_parameter("image_topic").value), self.image_callback, 10)
        self.timer = self.create_timer(0.05, self.timer_callback)

        self.input_thread = threading.Thread(target=self.stdin_loop, daemon=True)
        self.input_thread.start()

        self.get_logger().info(f"🚀 Charuco Calib Started: {self.cols}x{self.rows}")
        self.print_help()

    def print_help(self):
        print("\n================ Charuco Calibration CLI ================")
        print("s : save current frame (if Charuco board is detected)")
        print("c : run calibration from saved images")
        print("q : quit")
        print("========================================================\n")

    def stdin_loop(self):
        while True:
            try:
                cmd = input("> ").strip().lower()
                self.cmd_queue.put(cmd)
                if cmd == "q": break
            except: break

    def image_callback(self, msg: Image):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        with self.lock:
            self.latest_frame = frame.copy()

    def find_charuco(self, gray):
        charuco_corners, charuco_ids, _, _ = self.detector.detectBoard(gray)
        if charuco_ids is not None and len(charuco_ids) >= 4:
            return True, charuco_corners, charuco_ids
        return False, None, None

    def save_current_frame(self):
        with self.lock:
            if self.latest_frame is None: return
            frame = self.latest_frame.copy()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        found, _, _ = self.find_charuco(gray)

        if not found:
            self.get_logger().warning("Charuco board NOT detected, frame not saved")
            return

        idx = len(list(Path(self.save_dir).glob("*.jpg")))
        out_path = os.path.join(self.save_dir, f"calib_{idx:03d}.jpg")
        cv2.imwrite(out_path, frame)
        self.get_logger().info(f"📸 saved: {out_path}")

    def run_calibration(self):
        image_paths = sorted([str(p) for p in Path(self.save_dir).glob("*.jpg")])
        if not image_paths:
            self.get_logger().warning("no images found")
            return

        all_charuco_corners = []
        all_charuco_ids = []
        image_size = None

        self.get_logger().info("Processing images...")
        for path in image_paths:
            img = cv2.imread(path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            if image_size is None: image_size = gray.shape[::-1]

            found, corners, ids = self.find_charuco(gray)
            
            # [수정] 여기서는 터미널 알림 status 체크를 하지 않습니다. (파일 처리이므로)
            if found:
                all_charuco_corners.append(corners)
                all_charuco_ids.append(ids)
                vis = img.copy()
                aruco.drawDetectedCornersCharuco(vis, corners, ids)
                cv2.imwrite(str(self.debug_corners_dir / Path(path).name), vis)
                self.get_logger().info(f"[OK] {path}")
            else:
                self.get_logger().warning(f"[MISS] {path}")

        if len(all_charuco_corners) < 10:
            self.get_logger().warning(f"Not enough valid images ({len(all_charuco_corners)})")
            return

        rms, camera_matrix, dist_coeffs, rvecs, tvecs = aruco.calibrateCameraCharuco(
            charucoCorners=all_charuco_corners,
            charucoIds=all_charuco_ids,
            board=self.board,
            imageSize=image_size,
            cameraMatrix=None,
            distCoeffs=None
        )

        fs = cv2.FileStorage(self.output_yaml, cv2.FILE_STORAGE_WRITE)
        fs.write("image_width", image_size[0])
        fs.write("image_height", image_size[1])
        fs.write("camera_matrix", camera_matrix)
        fs.write("dist_coeffs", dist_coeffs)
        fs.write("rms", float(rms))
        fs.release()

        self.get_logger().info(f"✅ Calibration Done! RMS: {rms:.6f}")

    def timer_callback(self):
        while not self.cmd_queue.empty():
            cmd = self.cmd_queue.get()
            if cmd == "s": self.save_current_frame()
            elif cmd == "c": self.run_calibration()
            elif cmd == "q": rclpy.shutdown(); return

        if self.preview:
            with self.lock:
                frame = self.latest_frame.copy() if self.latest_frame is not None else None
            
            if frame is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                found, corners, ids = self.find_charuco(gray)
                
                # [수정] 실시간 알림은 여기서만 수행합니다.
                if found != self.last_found_status:
                    if found:
                        self.get_logger().info(f"✨ Charuco Board Detected! (Corners: {len(ids)})")
                    else:
                        self.get_logger().warn("❌ Board Lost")
                    self.last_found_status = found

                vis = frame.copy()
                status, color = ("Detected", (0, 255, 0)) if found else ("NOT Detected", (0, 0, 255))
                if found: aruco.drawDetectedCornersCharuco(vis, corners, ids)
                cv2.putText(vis, status, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)
                cv2.imshow("Charuco_Calib_Preview", vis)
                cv2.waitKey(1)

def main():
    rclpy.init()
    node = CameraCalibCliNode()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        if rclpy.ok(): rclpy.shutdown()

if __name__ == "__main__":
    main()