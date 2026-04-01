# camera_calib_cli_node.py

import os
import cv2
import queue
import threading
from pathlib import Path

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2.aruco as aruco


class CameraCalibCliNode(Node):
    def __init__(self):
        super().__init__("camera_calib_cli_node")

        # -----------------------------
        # parameters
        # -----------------------------
        self.declare_parameter("image_topic", "/camera/color/image_raw")
        self.declare_parameter("save_dir", "./calib_images")
        self.declare_parameter("output_yaml", "./camera_intrinsics.yaml")

        # 보드 spec
        self.declare_parameter("cols", 11)
        self.declare_parameter("rows", 6)
        self.declare_parameter("square_size", 0.05)
        self.declare_parameter("marker_size", 0.037)

        self.declare_parameter("preview", True)
        self.declare_parameter("min_corners_save", 8)
        self.declare_parameter("min_corners_calib", 4)

        image_topic = str(self.get_parameter("image_topic").value)
        self.save_dir = str(self.get_parameter("save_dir").value)
        self.output_yaml = str(self.get_parameter("output_yaml").value)

        self.cols = int(self.get_parameter("cols").value)
        self.rows = int(self.get_parameter("rows").value)
        self.square_size = float(self.get_parameter("square_size").value)
        self.marker_size = float(self.get_parameter("marker_size").value)

        self.preview = bool(self.get_parameter("preview").value)
        self.min_corners_save = int(self.get_parameter("min_corners_save").value)
        self.min_corners_calib = int(self.get_parameter("min_corners_calib").value)

        # -----------------------------
        # aruco / charuco setup
        # -----------------------------
        self.dictionary = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)

        # OpenCV version compatibility
        self.board = self._create_charuco_board(
            self.cols,
            self.rows,
            self.square_size,
            self.marker_size,
            self.dictionary,
        )

        self.params = self._create_detector_parameters()
        self.use_charuco_detector = hasattr(aruco, "CharucoDetector")

        if self.use_charuco_detector:
            try:
                self.detector = aruco.CharucoDetector(
                    self.board,
                    detectorParams=self.params
                )
            except TypeError:
                # 일부 버전은 keyword 인자 형태가 다를 수 있음
                self.detector = aruco.CharucoDetector(self.board)
        else:
            self.detector = None

        # -----------------------------
        # runtime state
        # -----------------------------
        Path(self.save_dir).mkdir(parents=True, exist_ok=True)
        self.debug_corners_dir = Path(self.save_dir) / "debug_corners"
        self.debug_corners_dir.mkdir(parents=True, exist_ok=True)

        self.bridge = CvBridge()
        self.latest_frame = None
        self.lock = threading.Lock()
        self.cmd_queue = queue.Queue()
        self.last_found_status = None

        self.sub = self.create_subscription(
            Image,
            image_topic,
            self.image_callback,
            10
        )
        self.timer = self.create_timer(0.05, self.timer_callback)

        self.input_thread = threading.Thread(target=self.stdin_loop, daemon=True)
        self.input_thread.start()

        self.get_logger().info(
            f"Charuco Calib Started | board={self.cols}x{self.rows} "
            f"| detector_api={'new' if self.use_charuco_detector else 'legacy'}"
        )
        self.print_help()

    # --------------------------------------------------
    # setup helpers
    # --------------------------------------------------
    def _create_charuco_board(self, cols, rows, square_size, marker_size, dictionary):
        """
        OpenCV version compatibility:
        - newer: aruco.CharucoBoard((cols, rows), ...)
        - older: aruco.CharucoBoard_create(cols, rows, ...)
        """
        if hasattr(aruco, "CharucoBoard"):
            try:
                return aruco.CharucoBoard(
                    (cols, rows),
                    square_size,
                    marker_size,
                    dictionary
                )
            except Exception:
                pass

        if hasattr(aruco, "CharucoBoard_create"):
            return aruco.CharucoBoard_create(
                cols,
                rows,
                square_size,
                marker_size,
                dictionary
            )

        raise RuntimeError(
            "Your OpenCV aruco module does not support CharucoBoard. "
            "Install opencv-contrib-python / python3-opencv with aruco support."
        )

    def _create_detector_parameters(self):
        """
        OpenCV version compatibility:
        - newer: aruco.DetectorParameters()
        - older: aruco.DetectorParameters_create()
        """
        if hasattr(aruco, "DetectorParameters"):
            params = aruco.DetectorParameters()
        elif hasattr(aruco, "DetectorParameters_create"):
            params = aruco.DetectorParameters_create()
        else:
            raise RuntimeError("aruco DetectorParameters API not found")

        # optional tuning
        if hasattr(params, "adaptiveThreshWinSizeMin"):
            params.adaptiveThreshWinSizeMin = 3
        if hasattr(params, "adaptiveThreshWinSizeMax"):
            params.adaptiveThreshWinSizeMax = 23
        if hasattr(params, "adaptiveThreshWinSizeStep"):
            params.adaptiveThreshWinSizeStep = 10
        if hasattr(params, "minMarkerPerimeterRate"):
            params.minMarkerPerimeterRate = 0.03
        if hasattr(params, "cornerRefinementMethod") and hasattr(aruco, "CORNER_REFINE_SUBPIX"):
            params.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX

        return params

    # --------------------------------------------------
    # CLI
    # --------------------------------------------------
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
                if cmd == "q":
                    break
            except Exception:
                break

    # --------------------------------------------------
    # ROS image callback
    # --------------------------------------------------
    def image_callback(self, msg: Image):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        with self.lock:
            self.latest_frame = frame.copy()

    # --------------------------------------------------
    # detection
    # --------------------------------------------------
    def find_charuco(self, gray):
        """
        Returns:
            found(bool), charuco_corners, charuco_ids, n_markers, n_charuco
        """
        # New API path
        if self.use_charuco_detector and self.detector is not None:
            result = self.detector.detectBoard(gray)

            # 버전에 따라 반환 개수가 다를 수 있어서 방어적으로 처리
            if isinstance(result, tuple):
                if len(result) == 4:
                    charuco_corners, charuco_ids, marker_corners, marker_ids = result
                elif len(result) == 3:
                    charuco_corners, charuco_ids, marker_corners = result
                    marker_ids = None
                else:
                    charuco_corners, charuco_ids = result[0], result[1]
                    marker_corners, marker_ids = None, None
            else:
                charuco_corners, charuco_ids = None, None
                marker_corners, marker_ids = None, None

        # Legacy API path
        else:
            marker_corners, marker_ids, _ = aruco.detectMarkers(
                gray,
                self.dictionary,
                parameters=self.params
            )

            if marker_ids is None or len(marker_ids) == 0:
                return False, None, None, 0, 0

            interp = aruco.interpolateCornersCharuco(
                markerCorners=marker_corners,
                markerIds=marker_ids,
                image=gray,
                board=self.board
            )

            # 보통 retval, charuco_corners, charuco_ids
            if interp is None or len(interp) < 3:
                return False, None, None, len(marker_ids), 0

            retval, charuco_corners, charuco_ids = interp
            if retval is None or retval <= 0 or charuco_ids is None:
                return False, None, None, len(marker_ids), 0

        n_markers = 0 if marker_ids is None else len(marker_ids)
        n_charuco = 0 if charuco_ids is None else len(charuco_ids)

        found = n_charuco >= self.min_corners_calib
        return found, charuco_corners, charuco_ids, n_markers, n_charuco

    # --------------------------------------------------
    # save frame
    # --------------------------------------------------
    def save_current_frame(self):
        with self.lock:
            if self.latest_frame is None:
                self.get_logger().warning("No frame received yet")
                return
            frame = self.latest_frame.copy()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        found, _, _, n_markers, n_charuco = self.find_charuco(gray)

        if n_charuco < self.min_corners_save:
            self.get_logger().warning(
                f"Charuco weak detection - markers={n_markers}, charuco={n_charuco}, frame not saved"
            )
            return

        idx = len(list(Path(self.save_dir).glob("*.jpg")))
        out_path = os.path.join(self.save_dir, f"calib_{idx:03d}.jpg")
        ok = cv2.imwrite(out_path, frame)

        if ok:
            self.get_logger().info(
                f"saved: {out_path} | markers={n_markers}, charuco={n_charuco}"
            )
        else:
            self.get_logger().error(f"failed to save image: {out_path}")

    # --------------------------------------------------
    # calibration
    # --------------------------------------------------
    def run_calibration(self):
        image_paths = sorted([str(p) for p in Path(self.save_dir).glob("*.jpg")])
        if not image_paths:
            self.get_logger().warning("no images found")
            return

        all_charuco_corners = []
        all_charuco_ids = []
        image_size = None

        self.get_logger().info(f"Processing {len(image_paths)} images...")

        for path in image_paths:
            img = cv2.imread(path)
            if img is None:
                self.get_logger().warning(f"[MISS] failed to read image: {path}")
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            if image_size is None:
                image_size = gray.shape[::-1]

            found, corners, ids, n_markers, n_charuco = self.find_charuco(gray)

            if found:
                all_charuco_corners.append(corners)
                all_charuco_ids.append(ids)

                vis = img.copy()
                try:
                    aruco.drawDetectedCornersCharuco(vis, corners, ids)
                except Exception:
                    pass
                cv2.imwrite(str(self.debug_corners_dir / Path(path).name), vis)

                self.get_logger().info(
                    f"[OK] {path} | markers={n_markers}, charuco={n_charuco}"
                )
            else:
                self.get_logger().warning(
                    f"[MISS] {path} | markers={n_markers}, charuco={n_charuco}"
                )

        if len(all_charuco_corners) < 10:
            self.get_logger().warning(
                f"Not enough valid images ({len(all_charuco_corners)})"
            )
            return

        try:
            rms, camera_matrix, dist_coeffs, rvecs, tvecs = aruco.calibrateCameraCharuco(
                charucoCorners=all_charuco_corners,
                charucoIds=all_charuco_ids,
                board=self.board,
                imageSize=image_size,
                cameraMatrix=None,
                distCoeffs=None
            )
        except TypeError:
            # 일부 OpenCV 버전은 positional 인자 선호
            rms, camera_matrix, dist_coeffs, rvecs, tvecs = aruco.calibrateCameraCharuco(
                all_charuco_corners,
                all_charuco_ids,
                self.board,
                image_size,
                None,
                None
            )

        fs = cv2.FileStorage(self.output_yaml, cv2.FILE_STORAGE_WRITE)
        fs.write("image_width", image_size[0])
        fs.write("image_height", image_size[1])
        fs.write("camera_matrix", camera_matrix)
        fs.write("dist_coeffs", dist_coeffs)
        fs.write("rms", float(rms))
        fs.release()

        self.get_logger().info(f"Calibration Done! RMS: {rms:.6f}")
        self.get_logger().info(f"Saved to: {self.output_yaml}")

    # --------------------------------------------------
    # timer / preview
    # --------------------------------------------------
    def timer_callback(self):
        while not self.cmd_queue.empty():
            cmd = self.cmd_queue.get()

            if cmd == "s":
                self.save_current_frame()
            elif cmd == "c":
                self.run_calibration()
            elif cmd == "q":
                rclpy.shutdown()
                return

        if not self.preview:
            return

        with self.lock:
            frame = self.latest_frame.copy() if self.latest_frame is not None else None

        if frame is None:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        found, corners, ids, n_markers, n_charuco = self.find_charuco(gray)

        if found != self.last_found_status:
            if found:
                self.get_logger().info(
                    f"Board detected | markers={n_markers}, charuco={n_charuco}"
                )
            else:
                self.get_logger().warning("Board lost")
            self.last_found_status = found

        vis = frame.copy()
        if found and corners is not None and ids is not None:
            try:
                aruco.drawDetectedCornersCharuco(vis, corners, ids)
            except Exception:
                pass

        status = f"markers={n_markers}, charuco={n_charuco}"
        color = (0, 255, 0) if found else (0, 0, 255)

        cv2.putText(
            vis,
            status,
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            color,
            2
        )
        cv2.imshow("Charuco_Calib_Preview", vis)
        cv2.waitKey(1)


def main():
    rclpy.init()
    node = CameraCalibCliNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()