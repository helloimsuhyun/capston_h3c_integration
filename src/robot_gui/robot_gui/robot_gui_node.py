#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import math
import threading
from typing import Optional

import cv2
import yaml
import numpy as np

import rclpy
from rclpy.node import Node

from cv_bridge import CvBridge
from geometry_msgs.msg import Pose2D
from sensor_msgs.msg import Image
from std_msgs.msg import String, Bool

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QSizePolicy,
)


# ==========================================================
# Shared GUI state
# ==========================================================
class GuiState:
    def __init__(self):
        self.latest_frame = None

        self.robot_x: Optional[float] = None
        self.robot_y: Optional[float] = None
        self.robot_yaw: Optional[float] = None
        self.robot_status: str = "unknown"

        self.goal_x: Optional[float] = None
        self.goal_y: Optional[float] = None
        self.goal_yaw: Optional[float] = None
        self.next_place_id: str = "-"

        self.follow_state: str = "unknown"
        self.auth_ready: bool = False
        self.patrol_command: str = "unknown"

        self.yolo_enable: bool = False
        self.audio_upload_enable: bool = True
        self.audio_allowed_labels: str = "ALL"

        # Map state
        self.map_image = None
        self.map_resolution: Optional[float] = None
        self.map_origin_x: Optional[float] = None
        self.map_origin_y: Optional[float] = None
        self.map_origin_yaw: float = 0.0
        self.map_path: str = ""


# ==========================================================
# ROS subscriber node
# ==========================================================
class RobotGuiRosNode(Node):
    def __init__(self, state: GuiState):
        super().__init__("robot_gui_node")
        self.state = state
        self.bridge = CvBridge()
        self.lock = threading.Lock()

        self.declare_parameter("annotated_topic", "/person_tracking/annotated")
        self.declare_parameter("robot_pose_topic", "/robot_pose")
        self.declare_parameter("robot_status_topic", "/robot_status")
        self.declare_parameter("goal_pose_topic", "/goal_pose_2d")
        self.declare_parameter("next_place_topic", "/next_place_id")
        self.declare_parameter("follow_state_topic", "/person_tracking/follow_state")
        self.declare_parameter("auth_ready_topic", "/auth_ready")
        self.declare_parameter("patrol_command_topic", "/patrol/command")

        self.declare_parameter("yolo_enable_topic", "/person_tracking/enable")
        self.declare_parameter("audio_upload_enable_topic", "/sound/upload_enable")
        self.declare_parameter("audio_allowed_labels_topic", "/sound/allowed_labels")

        # 예: /home/choisuhyun/maps/map.yaml
        self.declare_parameter("map_yaml_path", "")

        annotated_topic = self.get_parameter("annotated_topic").value
        robot_pose_topic = self.get_parameter("robot_pose_topic").value
        robot_status_topic = self.get_parameter("robot_status_topic").value
        goal_pose_topic = self.get_parameter("goal_pose_topic").value
        next_place_topic = self.get_parameter("next_place_topic").value
        follow_state_topic = self.get_parameter("follow_state_topic").value
        auth_ready_topic = self.get_parameter("auth_ready_topic").value
        patrol_command_topic = self.get_parameter("patrol_command_topic").value

        yolo_enable_topic = self.get_parameter("yolo_enable_topic").value
        audio_upload_enable_topic = self.get_parameter("audio_upload_enable_topic").value
        audio_allowed_labels_topic = self.get_parameter("audio_allowed_labels_topic").value

        map_yaml_path = str(self.get_parameter("map_yaml_path").value)
        self.load_map_yaml(map_yaml_path)

        self.create_subscription(Image, annotated_topic, self.annotated_cb, 10)
        self.create_subscription(Pose2D, robot_pose_topic, self.robot_pose_cb, 10)
        self.create_subscription(String, robot_status_topic, self.robot_status_cb, 10)
        self.create_subscription(Pose2D, goal_pose_topic, self.goal_pose_cb, 10)
        self.create_subscription(String, next_place_topic, self.next_place_cb, 10)
        self.create_subscription(String, follow_state_topic, self.follow_state_cb, 10)
        self.create_subscription(Bool, auth_ready_topic, self.auth_ready_cb, 10)
        self.create_subscription(String, patrol_command_topic, self.patrol_command_cb, 10)

        self.create_subscription(Bool, yolo_enable_topic, self.yolo_enable_cb, 10)
        self.create_subscription(Bool, audio_upload_enable_topic, self.audio_upload_enable_cb, 10)
        self.create_subscription(String, audio_allowed_labels_topic, self.audio_allowed_labels_cb, 10)

        self.get_logger().info("Robot GUI ROS node started")
        self.get_logger().info(f"camera={annotated_topic}")
        self.get_logger().info(f"robot_pose={robot_pose_topic}, goal_pose={goal_pose_topic}")
        self.get_logger().info(f"map_yaml_path={map_yaml_path}")

    # --------------------------
    # Map loading
    # --------------------------
    def load_map_yaml(self, map_yaml_path: str):
        if not map_yaml_path:
            self.get_logger().warn("[MAP] map_yaml_path is empty. Map viewer disabled.")
            return

        if not os.path.isfile(map_yaml_path):
            self.get_logger().warn(f"[MAP] yaml not found: {map_yaml_path}")
            return

        try:
            with open(map_yaml_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}

            image_rel = cfg.get("image")
            resolution = float(cfg.get("resolution"))
            origin = cfg.get("origin", [0.0, 0.0, 0.0])

            origin_x = float(origin[0])
            origin_y = float(origin[1])
            origin_yaw = float(origin[2]) if len(origin) >= 3 else 0.0

            yaml_dir = os.path.dirname(map_yaml_path)
            image_path = image_rel
            if not os.path.isabs(image_path):
                image_path = os.path.join(yaml_dir, image_rel)

            if not os.path.isfile(image_path):
                self.get_logger().warn(f"[MAP] image not found: {image_path}")
                return

            img = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if img is None:
                self.get_logger().warn(f"[MAP] failed to load image: {image_path}")
                return

            with self.lock:
                self.state.map_image = img
                self.state.map_resolution = resolution
                self.state.map_origin_x = origin_x
                self.state.map_origin_y = origin_y
                self.state.map_origin_yaw = origin_yaw
                self.state.map_path = image_path

            self.get_logger().info(
                f"[MAP] loaded image={image_path}, "
                f"resolution={resolution}, origin=({origin_x}, {origin_y}, {origin_yaw})"
            )

        except Exception as e:
            self.get_logger().warn(f"[MAP] load failed: {e}")

    # --------------------------
    # ROS callbacks
    # --------------------------
    def annotated_cb(self, msg: Image):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            self.state.latest_frame = frame.copy()
        except Exception as e:
            self.get_logger().warn(f"Failed to convert annotated image: {e}")

    def robot_pose_cb(self, msg: Pose2D):
        self.state.robot_x = float(msg.x)
        self.state.robot_y = float(msg.y)
        self.state.robot_yaw = float(msg.theta)

    def robot_status_cb(self, msg: String):
        value = msg.data.strip()
        self.state.robot_status = value if value else "idle"

    def goal_pose_cb(self, msg: Pose2D):
        self.state.goal_x = float(msg.x)
        self.state.goal_y = float(msg.y)
        self.state.goal_yaw = float(msg.theta)

    def next_place_cb(self, msg: String):
        value = msg.data.strip()
        self.state.next_place_id = value if value else "-"

    def follow_state_cb(self, msg: String):
        value = msg.data.strip()
        self.state.follow_state = value if value else "unknown"

    def auth_ready_cb(self, msg: Bool):
        self.state.auth_ready = bool(msg.data)

    def patrol_command_cb(self, msg: String):
        value = msg.data.strip()
        self.state.patrol_command = value if value else "unknown"

    def yolo_enable_cb(self, msg: Bool):
        self.state.yolo_enable = bool(msg.data)

    def audio_upload_enable_cb(self, msg: Bool):
        self.state.audio_upload_enable = bool(msg.data)

    def audio_allowed_labels_cb(self, msg: String):
        value = msg.data.strip()
        if not value or value == "[]":
            self.state.audio_allowed_labels = "ALL"
            return

        try:
            labels = json.loads(value)
            if isinstance(labels, list) and len(labels) > 0:
                self.state.audio_allowed_labels = ", ".join(map(str, labels))
            else:
                self.state.audio_allowed_labels = "ALL"
        except Exception:
            self.state.audio_allowed_labels = value


# ==========================================================
# PyQt GUI
# ==========================================================
class SecurityRobotGui(QWidget):
    def __init__(self, state: GuiState):
        super().__init__()
        self.state = state

        self.setWindowTitle("Security Patrol Robot GUI")
        self.resize(1250, 900)

        self.camera_label = QLabel("Waiting for /person_tracking/annotated ...")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumHeight(420)
        self.camera_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.camera_label.setStyleSheet(
            "background-color: #111; color: #ddd; border-radius: 8px; padding: 8px;"
        )

        self.map_label = QLabel("Waiting for map ...")
        self.map_label.setAlignment(Qt.AlignCenter)
        self.map_label.setMinimumHeight(300)
        self.map_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.map_label.setStyleSheet(
            "background-color: #222; color: #ddd; border-radius: 8px; padding: 8px;"
        )

        self.robot_pose_label = QLabel()
        self.robot_status_label = QLabel()
        self.goal_pose_label = QLabel()
        self.next_place_label = QLabel()
        self.follow_state_label = QLabel()
        self.auth_state_label = QLabel()
        self.command_label = QLabel()

        self.yolo_enable_label = QLabel()
        self.audio_upload_label = QLabel()
        self.audio_labels_label = QLabel()
        self.map_info_label = QLabel()

        for label in [
            self.robot_pose_label,
            self.robot_status_label,
            self.goal_pose_label,
            self.next_place_label,
            self.follow_state_label,
            self.auth_state_label,
            self.command_label,
            self.yolo_enable_label,
            self.audio_upload_label,
            self.audio_labels_label,
            self.map_info_label,
        ]:
            label.setFont(QFont("DejaVu Sans", 11))
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self._build_layout()

        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.refresh_ui)
        self.ui_timer.start(100)

    def _build_layout(self):
        root = QVBoxLayout()
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        title = QLabel("Indoor Security Patrol Robot")
        title.setFont(QFont("DejaVu Sans", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        root.addWidget(title)

        top = QHBoxLayout()
        top.setSpacing(10)
        top.addWidget(self.camera_label, stretch=3)
        top.addWidget(self.map_label, stretch=2)
        root.addLayout(top, stretch=5)

        bottom = QHBoxLayout()
        bottom.setSpacing(10)

        robot_box = QGroupBox("Robot State")
        robot_layout = QVBoxLayout()
        robot_layout.addWidget(self.robot_pose_label)
        robot_layout.addWidget(self.robot_status_label)
        robot_layout.addWidget(self.map_info_label)
        robot_box.setLayout(robot_layout)

        goal_box = QGroupBox("Goal State")
        goal_layout = QVBoxLayout()
        goal_layout.addWidget(self.goal_pose_label)
        goal_layout.addWidget(self.next_place_label)
        goal_box.setLayout(goal_layout)

        perception_box = QGroupBox("Tracking / Auth / Command")
        perception_layout = QVBoxLayout()
        perception_layout.addWidget(self.follow_state_label)
        perception_layout.addWidget(self.auth_state_label)
        perception_layout.addWidget(self.command_label)
        perception_layout.addWidget(self.yolo_enable_label)
        perception_layout.addWidget(self.audio_upload_label)
        perception_layout.addWidget(self.audio_labels_label)
        perception_box.setLayout(perception_layout)

        bottom.addWidget(robot_box, stretch=1)
        bottom.addWidget(goal_box, stretch=1)
        bottom.addWidget(perception_box, stretch=1)

        root.addLayout(bottom, stretch=2)
        self.setLayout(root)

    # --------------------------
    # Formatting
    # --------------------------
    @staticmethod
    def fmt_pose(x: Optional[float], y: Optional[float], yaw: Optional[float]) -> str:
        if x is None or y is None or yaw is None:
            return "x: - | y: - | yaw: -"
        return f"x: {x:.3f} | y: {y:.3f} | yaw: {yaw:.3f}"

    @staticmethod
    def compute_auth_text(follow_state: str, auth_ready: bool) -> str:
        normalized = (follow_state or "").strip().upper()

        if normalized == "TRACKING" and auth_ready:
            return "RFID 대기"
        if normalized == "TRACKING" and not auth_ready:
            return "인증 대기 아님"
        return "idle"

    @staticmethod
    def bool_text(value: bool) -> str:
        return "ON" if value else "OFF"

    # --------------------------
    # Map transform / drawing
    # --------------------------
    def world_to_pixel(self, x: float, y: float):
        resolution = self.state.map_resolution
        origin_x = self.state.map_origin_x
        origin_y = self.state.map_origin_y
        map_img = self.state.map_image

        if resolution is None or origin_x is None or origin_y is None or map_img is None:
            return None

        h, w = map_img.shape[:2]

        px = int((x - origin_x) / resolution)
        py = int(h - ((y - origin_y) / resolution))

        return px, py

    def draw_text_with_outline(self, img, text: str, pos, color, scale=0.6, thickness=2):
        outline = (255, 255, 255)
        cv2.putText(
            img,
            text,
            pos,
            cv2.FONT_HERSHEY_SIMPLEX,
            scale,
            outline,
            thickness + 2,
            cv2.LINE_AA,
        )
        cv2.putText(
            img,
            text,
            pos,
            cv2.FONT_HERSHEY_SIMPLEX,
            scale,
            color,
            thickness,
            cv2.LINE_AA,
        )

    def draw_robot_marker(self, img, x: float, y: float, yaw: float):
        pix = self.world_to_pixel(x, y)
        if pix is None:
            return

        px, py = pix
        h, w = img.shape[:2]

        if px < 0 or px >= w or py < 0 or py >= h:
            return

        color = (255, 80, 20)       # BGR: bright blue
        outline = (255, 255, 255)

        # 방향 삼각형
        tip_len = 22
        rear_len = 13
        spread = 2.45

        tip = np.array([
            px + tip_len * math.cos(yaw),
            py - tip_len * math.sin(yaw),
        ])

        left = np.array([
            px + rear_len * math.cos(yaw + spread),
            py - rear_len * math.sin(yaw + spread),
        ])

        right = np.array([
            px + rear_len * math.cos(yaw - spread),
            py - rear_len * math.sin(yaw - spread),
        ])

        pts = np.array([tip, left, right], dtype=np.int32)

        # 외곽선 먼저, 내부 채우기
        cv2.polylines(img, [pts], True, outline, 5, cv2.LINE_AA)
        cv2.fillPoly(img, [pts], color, lineType=cv2.LINE_AA)
        cv2.polylines(img, [pts], True, outline, 2, cv2.LINE_AA)

        # 현재 위치 중심점 + 강조 링
        cv2.circle(img, (px, py), 4, outline, -1)
        cv2.circle(img, (px, py), 24, color, 2, cv2.LINE_AA)

        self.draw_text_with_outline(
            img,
            "ROBOT",
            (px + 18, py - 18),
            color,
            scale=0.6,
            thickness=2,
        )

    def draw_goal_marker(self, img, x: float, y: float, yaw: float):
        pix = self.world_to_pixel(x, y)
        if pix is None:
            return

        px, py = pix
        h, w = img.shape[:2]

        if px < 0 or px >= w or py < 0 or py >= h:
            return

        color = (40, 40, 255)      # BGR: red
        outline = (255, 255, 255)

        # 깃대
        pole_top = (px, py - 38)
        pole_bottom = (px, py + 16)
        cv2.line(img, pole_top, pole_bottom, outline, 6, cv2.LINE_AA)
        cv2.line(img, pole_top, pole_bottom, color, 3, cv2.LINE_AA)

        # 깃발
        flag_pts = np.array([
            [px, py - 38],
            [px + 38, py - 27],
            [px, py - 16],
        ], dtype=np.int32)

        cv2.polylines(img, [flag_pts], True, outline, 5, cv2.LINE_AA)
        cv2.fillPoly(img, [flag_pts], color, lineType=cv2.LINE_AA)
        cv2.polylines(img, [flag_pts], True, outline, 2, cv2.LINE_AA)

        # 목표 지점 링
        cv2.circle(img, (px, py), 12, color, 3, cv2.LINE_AA)
        cv2.circle(img, (px, py), 5, outline, -1)

        # 목표 yaw 방향 작은 화살표
        arrow_len = 28
        end_x = int(px + arrow_len * math.cos(yaw))
        end_y = int(py - arrow_len * math.sin(yaw))

        cv2.arrowedLine(
            img,
            (px, py),
            (end_x, end_y),
            color,
            2,
            tipLength=0.35,
        )

        self.draw_text_with_outline(
            img,
            "GOAL",
            (px + 18, py + 36),
            color,
            scale=0.6,
            thickness=2,
        )

    def refresh_map(self):
        map_img = self.state.map_image
        if map_img is None:
            self.map_label.setText("Map not loaded")
            return

        try:
            vis = map_img.copy()

            # 현재 로봇 위치: 파란 삼각형
            if (
                self.state.robot_x is not None
                and self.state.robot_y is not None
                and self.state.robot_yaw is not None
            ):
                self.draw_robot_marker(
                    vis,
                    self.state.robot_x,
                    self.state.robot_y,
                    self.state.robot_yaw,
                )

            # 목표 위치: 빨간 깃발
            if (
                self.state.goal_x is not None
                and self.state.goal_y is not None
                and self.state.goal_yaw is not None
            ):
                self.draw_goal_marker(
                    vis,
                    self.state.goal_x,
                    self.state.goal_y,
                    self.state.goal_yaw,
                )

            rgb = cv2.cvtColor(vis, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)

            pixmap = QPixmap.fromImage(qimg)
            pixmap = pixmap.scaled(
                self.map_label.width(),
                self.map_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )

            self.map_label.setPixmap(pixmap)

        except Exception:
            self.map_label.setText("Map rendering failed")

    # --------------------------
    # Refresh
    # --------------------------
    def refresh_ui(self):
        self.refresh_camera()
        self.refresh_map()

        self.robot_pose_label.setText(
            "Current Pose\n" + self.fmt_pose(
                self.state.robot_x,
                self.state.robot_y,
                self.state.robot_yaw,
            )
        )
        self.robot_status_label.setText(f"Robot Status\n{self.state.robot_status}")

        self.goal_pose_label.setText(
            "Goal Pose\n" + self.fmt_pose(
                self.state.goal_x,
                self.state.goal_y,
                self.state.goal_yaw,
            )
        )
        self.next_place_label.setText(f"Next Place\n{self.state.next_place_id}")

        self.follow_state_label.setText(f"Tracking State\n{self.state.follow_state}")
        self.auth_state_label.setText(
            "Auth State\n" + self.compute_auth_text(
                self.state.follow_state,
                self.state.auth_ready,
            )
        )
        self.command_label.setText(f"Patrol Command\n{self.state.patrol_command}")

        self.yolo_enable_label.setText(
            f"YOLO Enable\n{self.bool_text(self.state.yolo_enable)}"
        )
        self.audio_upload_label.setText(
            f"Audio Upload Enable\n{self.bool_text(self.state.audio_upload_enable)}"
        )
        self.audio_labels_label.setText(
            f"Audio Labels\n{self.state.audio_allowed_labels}"
        )

        if self.state.map_image is None:
            self.map_info_label.setText("Map\nnot loaded")
        else:
            h, w = self.state.map_image.shape[:2]
            self.map_info_label.setText(
                f"Map\n"
                f"size: {w}x{h} px | res: {self.state.map_resolution} m/px\n"
                f"origin: ({self.state.map_origin_x}, {self.state.map_origin_y})"
            )

    def refresh_camera(self):
        frame = self.state.latest_frame
        if frame is None:
            return

        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)

            pixmap = QPixmap.fromImage(qimg)
            pixmap = pixmap.scaled(
                self.camera_label.width(),
                self.camera_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.camera_label.setPixmap(pixmap)
        except Exception:
            self.camera_label.setText("Camera frame rendering failed")


# ==========================================================
# Main
# ==========================================================
def main(args=None):
    rclpy.init(args=args)

    app = QApplication(sys.argv)
    state = GuiState()

    node = RobotGuiRosNode(state)
    gui = SecurityRobotGui(state)

    ros_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    ros_thread.start()

    gui.show()
    exit_code = app.exec_()

    node.destroy_node()
    rclpy.shutdown()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()