#camera_calib_cli_node.py

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


class CameraCalibCliNode(Node):
    def __init__(self):
        super().__init__("camera_calib_cli_node")

        self.declare_parameter("image_topic", "/camera/color/image_raw")
        self.declare_parameter("save_dir", "./calib_images")
        self.declare_parameter("output_yaml", "./camera_intrinsics.yaml")
        self.declare_parameter("output_npz", "./camera_intrinsics.npz")
        self.declare_parameter("cols", 11)               # 내부 코너 열 개수
        self.declare_parameter("rows", 6)               # 내부 코너 행 개수
        self.declare_parameter("square_size", 0.050)    # meter
        self.declare_parameter("preview", True)

        # 디버그 저장 옵션
        self.declare_parameter("save_debug_corners", True)
        self.declare_parameter("save_debug_reproj", True)
        self.declare_parameter("save_debug_undistort", True)
        self.declare_parameter("save_debug_txt", True)

        image_topic = str(self.get_parameter("image_topic").value)
        self.save_dir = str(self.get_parameter("save_dir").value)
        self.output_yaml = str(self.get_parameter("output_yaml").value)
        self.output_npz = str(self.get_parameter("output_npz").value)
        self.cols = int(self.get_parameter("cols").value)
        self.rows = int(self.get_parameter("rows").value)
        self.square_size = float(self.get_parameter("square_size").value)
        self.preview = bool(self.get_parameter("preview").value)

        self.save_debug_corners = bool(self.get_parameter("save_debug_corners").value)
        self.save_debug_reproj = bool(self.get_parameter("save_debug_reproj").value)
        self.save_debug_undistort = bool(self.get_parameter("save_debug_undistort").value)
        self.save_debug_txt = bool(self.get_parameter("save_debug_txt").value)

        Path(self.save_dir).mkdir(parents=True, exist_ok=True)

        self.debug_corners_dir = Path(self.save_dir) / "debug_corners"
        self.debug_reproj_dir = Path(self.save_dir) / "debug_reproj"
        self.debug_undistort_dir = Path(self.save_dir) / "debug_undistort"

        if self.save_debug_corners:
            self.debug_corners_dir.mkdir(parents=True, exist_ok=True)
        if self.save_debug_reproj:
            self.debug_reproj_dir.mkdir(parents=True, exist_ok=True)
        if self.save_debug_undistort:
            self.debug_undistort_dir.mkdir(parents=True, exist_ok=True)

        self.bridge = CvBridge()
        self.latest_frame = None
        self.latest_stamp = None
        self.lock = threading.Lock()
        self.cmd_queue = queue.Queue()

        self.sub = self.create_subscription(
            Image,
            image_topic,
            self.image_callback,
            10
        )

        self.timer = self.create_timer(0.05, self.timer_callback)

        self.input_thread = threading.Thread(target=self.stdin_loop, daemon=True)
        self.input_thread.start()

        self.get_logger().info("camera_calib_cli_node started")
        self.print_help()

    def print_help(self):
        print("\n================ Calibration CLI ================")
        print("s : save current frame if chessboard is detected")
        print("c : run calibration from saved images")
        print("h : help")
        print("q : quit")
        print("=================================================\n")

    def stdin_loop(self):
        while True:
            try:
                cmd = input("> ").strip().lower()
                self.cmd_queue.put(cmd)
                if cmd == "q":
                    break
            except EOFError:
                break
            except Exception:
                break

    def image_callback(self, msg: Image):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        with self.lock:
            self.latest_frame = frame.copy()
            self.latest_stamp = time.time()

    def find_chessboard(self, gray):
        pattern_size = (self.cols, self.rows)
        flags = (
            cv2.CALIB_CB_ADAPTIVE_THRESH
            + cv2.CALIB_CB_NORMALIZE_IMAGE
            + cv2.CALIB_CB_FAST_CHECK
        )
        found, corners = cv2.findChessboardCorners(gray, pattern_size, flags)

        if not found:
            return found, corners

        criteria = (
            cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
            30,
            0.001
        )
        corners = cv2.cornerSubPix(
            gray,
            corners,
            (11, 11),
            (-1, -1),
            criteria
        )
        return found, corners

    def save_current_frame(self):
        with self.lock:
            if self.latest_frame is None:
                self.get_logger().warning("no frame received yet")
                return
            frame = self.latest_frame.copy()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        found, corners = self.find_chessboard(gray)

        if not found:
            self.get_logger().warning("chessboard not detected, frame not saved")
            return

        idx = len(list(Path(self.save_dir).glob("*.jpg")))
        out_path = os.path.join(self.save_dir, f"calib_{idx:03d}.jpg")
        ok = cv2.imwrite(out_path, frame)
        if ok:
            self.get_logger().info(f"saved: {out_path}")
        else:
            self.get_logger().warning(f"failed to save: {out_path}")

    def collect_points_from_images(self, image_paths):
        pattern_size = (self.cols, self.rows)

        objp = np.zeros((self.cols * self.rows, 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.cols, 0:self.rows].T.reshape(-1, 2)
        objp *= self.square_size

        objpoints = []
        imgpoints = []
        valid_paths = []
        image_size = None

        for path in image_paths:
            img = cv2.imread(path)
            if img is None:
                self.get_logger().warning(f"failed to read: {path}")
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            if image_size is None:
                image_size = (gray.shape[1], gray.shape[0])

            found, corners = self.find_chessboard(gray)
            if found:
                objpoints.append(objp.copy())
                imgpoints.append(corners)
                valid_paths.append(path)
                self.get_logger().info(f"[OK] {path}")

                vis = img.copy()
                cv2.drawChessboardCorners(vis, pattern_size, corners, found)

                if self.save_debug_corners:
                    out_path = self.debug_corners_dir / Path(path).name
                    cv2.imwrite(str(out_path), vis)

                if self.preview:
                    cv2.imshow("calib_preview", vis)
                    cv2.waitKey(150)
            else:
                self.get_logger().warning(f"[MISS] {path}")

        if self.preview:
            cv2.destroyWindow("calib_preview")

        return objpoints, imgpoints, valid_paths, image_size

    def compute_reprojection_errors(self, objpoints, imgpoints, rvecs, tvecs, camera_matrix, dist_coeffs):
        per_view_errors = []
        total_error = 0.0

        for i in range(len(objpoints)):
            projected, _ = cv2.projectPoints(
                objpoints[i], rvecs[i], tvecs[i], camera_matrix, dist_coeffs
            )
            error = cv2.norm(imgpoints[i], projected, cv2.NORM_L2) / len(projected)
            per_view_errors.append(float(error))
            total_error += error

        mean_error = total_error / len(objpoints) if objpoints else None
        return mean_error, per_view_errors

    def save_yaml(self, image_size, camera_matrix, dist_coeffs, rms, per_view_errors):
        fs = cv2.FileStorage(self.output_yaml, cv2.FILE_STORAGE_WRITE)
        if not fs.isOpened():
            raise RuntimeError(f"failed to open yaml for write: {self.output_yaml}")

        fs.write("image_width", int(image_size[0]))
        fs.write("image_height", int(image_size[1]))
        fs.write("camera_matrix", camera_matrix)
        fs.write("dist_coeffs", dist_coeffs)
        fs.write("rms", float(rms))
        fs.write("per_view_errors", np.array(per_view_errors, dtype=np.float32))
        fs.release()

    def save_reprojection_debug(
        self,
        objpoints,
        imgpoints,
        rvecs,
        tvecs,
        camera_matrix,
        dist_coeffs,
        valid_paths,
        per_view_errors
    ):
        if not self.save_debug_reproj:
            return

        for i, path in enumerate(valid_paths):
            img = cv2.imread(path)
            if img is None:
                continue

            projected, _ = cv2.projectPoints(
                objpoints[i],
                rvecs[i],
                tvecs[i],
                camera_matrix,
                dist_coeffs
            )

            vis = img.copy()

            # 실제 검출 corner: 초록
            for p in imgpoints[i]:
                x, y = int(round(p[0][0])), int(round(p[0][1]))
                cv2.circle(vis, (x, y), 4, (0, 255, 0), -1)

            # 재투영 corner: 빨강
            for p in projected:
                x, y = int(round(p[0][0])), int(round(p[0][1]))
                cv2.circle(vis, (x, y), 2, (0, 0, 255), -1)

            cv2.putText(
                vis,
                f"err={per_view_errors[i]:.4f}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 255),
                2
            )
            cv2.putText(
                vis,
                "green=detected, red=reprojected",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 0),
                2
            )

            out_path = self.debug_reproj_dir / f"reproj_{i:03d}.jpg"
            cv2.imwrite(str(out_path), vis)

    def save_undistort_debug(self, camera_matrix, dist_coeffs, valid_paths):
        if not self.save_debug_undistort:
            return

        for i, path in enumerate(valid_paths):
            img = cv2.imread(path)
            if img is None:
                continue

            h, w = img.shape[:2]
            new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
                camera_matrix, dist_coeffs, (w, h), 0, (w, h)
            )
            undist = cv2.undistort(img, camera_matrix, dist_coeffs, None, new_camera_matrix)

            x, y, rw, rh = roi
            if rw > 0 and rh > 0:
                undist_crop = undist[y:y+rh, x:x+rw]
                undist_crop = cv2.resize(undist_crop, (w, h))
            else:
                undist_crop = undist

            combined = np.hstack([img, undist_crop])

            cv2.putText(
                combined,
                "Original",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 255),
                2
            )
            cv2.putText(
                combined,
                "Undistorted",
                (w + 20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 255),
                2
            )

            out_path = self.debug_undistort_dir / f"undist_{i:03d}.jpg"
            cv2.imwrite(str(out_path), combined)

    def save_debug_txt(self, rms, mean_error, per_view_errors, valid_paths, camera_matrix, dist_coeffs, image_size):
        if not self.save_debug_txt:
            return

        txt_path = Path(self.save_dir) / "calibration_debug.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("=== Camera Calibration Debug ===\n")
            f.write(f"image_width: {image_size[0]}\n")
            f.write(f"image_height: {image_size[1]}\n")
            f.write(f"valid_images: {len(valid_paths)}\n")
            f.write(f"rms: {rms}\n")
            f.write(f"mean_reprojection_error: {mean_error}\n\n")

            f.write("camera_matrix:\n")
            f.write(f"{camera_matrix}\n\n")

            f.write("dist_coeffs:\n")
            f.write(f"{dist_coeffs.ravel()}\n\n")

            f.write("per_view_errors:\n")
            for i, err in enumerate(per_view_errors):
                f.write(f"{i:03d}: {err:.6f}  {valid_paths[i]}\n")

    def run_calibration(self):
        image_paths = sorted([str(p) for p in Path(self.save_dir).glob("*.jpg")])

        if len(image_paths) == 0:
            self.get_logger().warning("no calibration images found")
            return

        self.get_logger().info(f"found {len(image_paths)} saved images")

        objpoints, imgpoints, valid_paths, image_size = self.collect_points_from_images(image_paths)

        if len(objpoints) < 8:
            self.get_logger().warning(
                f"not enough valid images for calibration: {len(objpoints)} (need about 8~15+)"
            )
            return

        rms, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            objpoints,
            imgpoints,
            image_size,
            None,
            None
        )

        mean_error, per_view_errors = self.compute_reprojection_errors(
            objpoints, imgpoints, rvecs, tvecs, camera_matrix, dist_coeffs
        )

        self.save_yaml(image_size, camera_matrix, dist_coeffs, rms, per_view_errors)

        np.savez(
            self.output_npz,
            image_width=image_size[0],
            image_height=image_size[1],
            camera_matrix=camera_matrix,
            dist_coeffs=dist_coeffs,
            rms=rms,
            mean_reprojection_error=mean_error,
            per_view_errors=np.array(per_view_errors, dtype=np.float32),
            valid_image_paths=np.array(valid_paths)
        )

        self.save_reprojection_debug(
            objpoints,
            imgpoints,
            rvecs,
            tvecs,
            camera_matrix,
            dist_coeffs,
            valid_paths,
            per_view_errors
        )

        self.save_undistort_debug(
            camera_matrix,
            dist_coeffs,
            valid_paths
        )

        self.save_debug_txt(
            rms,
            mean_error,
            per_view_errors,
            valid_paths,
            camera_matrix,
            dist_coeffs,
            image_size
        )

        self.get_logger().info("========== Calibration Result ==========")
        self.get_logger().info(f"valid images        : {len(valid_paths)}")
        self.get_logger().info(f"image size          : {image_size}")
        self.get_logger().info(f"RMS                 : {rms:.6f}")
        self.get_logger().info(f"mean reproj error   : {mean_error:.6f}")
        self.get_logger().info(f"saved yaml          : {self.output_yaml}")
        self.get_logger().info(f"saved npz           : {self.output_npz}")
        if self.save_debug_corners:
            self.get_logger().info(f"saved debug corners : {self.debug_corners_dir}")
        if self.save_debug_reproj:
            self.get_logger().info(f"saved debug reproj  : {self.debug_reproj_dir}")
        if self.save_debug_undistort:
            self.get_logger().info(f"saved undistort dbg : {self.debug_undistort_dir}")
        if self.save_debug_txt:
            self.get_logger().info(f"saved debug txt     : {Path(self.save_dir) / 'calibration_debug.txt'}")
        self.get_logger().info("========================================")

        print("\nCamera Matrix:")
        print(camera_matrix)
        print("\nDistortion Coeffs:")
        print(dist_coeffs.ravel())
        print()

    def timer_callback(self):
        while not self.cmd_queue.empty():
            cmd = self.cmd_queue.get()

            if cmd == "s":
                self.save_current_frame()
            elif cmd == "c":
                self.run_calibration()
            elif cmd == "h":
                self.print_help()
            elif cmd == "q":
                self.get_logger().info("quit requested")
                rclpy.shutdown()
                return

        if self.preview:
            with self.lock:
                frame = None if self.latest_frame is None else self.latest_frame.copy()

            if frame is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                found, corners = self.find_chessboard(gray)

                vis = frame.copy()
                if found:
                    cv2.drawChessboardCorners(vis, (self.cols, self.rows), corners, found)
                    cv2.putText(vis, "Chessboard detected", (20, 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                else:
                    cv2.putText(vis, "Chessboard NOT detected", (20, 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

                cv2.imshow("camera_calib_cli_node", vis)
                cv2.waitKey(1)


def main():
    rclpy.init()
    node = CameraCalibCliNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("KeyboardInterrupt received, shutting down.")
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()