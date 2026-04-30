#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ROS 2 onboard GUI for indoor security patrol robot.

Features
--------
1. YOLO annotated camera view
   - /person_tracking/annotated : sensor_msgs/Image

2. Robot current pose / goal pose / status
   - /robot_pose     : geometry_msgs/Pose2D
   - /robot_status   : std_msgs/String
   - /goal_pose_2d   : geometry_msgs/Pose2D
   - /next_place_id  : std_msgs/String

3. Tracking / secondary auth / patrol command status
   - /person_tracking/follow_state : std_msgs/String
   - /auth_ready                   : std_msgs/Bool
   - /patrol/command               : std_msgs/String

This GUI does not use HTTP polling. It only subscribes to currently published ROS topics.
"""

import sys
import threading
from typing import Optional

import cv2
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
    QGridLayout,
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


# ==========================================================
# ROS subscriber node
# ==========================================================
class RobotGuiRosNode(Node):
    def __init__(self, state: GuiState):
        super().__init__("robot_gui_node")
        self.state = state
        self.bridge = CvBridge()

        # Parameters for topic names
        self.declare_parameter("annotated_topic", "/person_tracking/annotated")
        self.declare_parameter("robot_pose_topic", "/robot_pose")
        self.declare_parameter("robot_status_topic", "/robot_status")
        self.declare_parameter("goal_pose_topic", "/goal_pose_2d")
        self.declare_parameter("next_place_topic", "/next_place_id")
        self.declare_parameter("follow_state_topic", "/person_tracking/follow_state")
        self.declare_parameter("auth_ready_topic", "/auth_ready")
        self.declare_parameter("patrol_command_topic", "/patrol/command")

        annotated_topic = self.get_parameter("annotated_topic").value
        robot_pose_topic = self.get_parameter("robot_pose_topic").value
        robot_status_topic = self.get_parameter("robot_status_topic").value
        goal_pose_topic = self.get_parameter("goal_pose_topic").value
        next_place_topic = self.get_parameter("next_place_topic").value
        follow_state_topic = self.get_parameter("follow_state_topic").value
        auth_ready_topic = self.get_parameter("auth_ready_topic").value
        patrol_command_topic = self.get_parameter("patrol_command_topic").value

        self.create_subscription(Image, annotated_topic, self.annotated_cb, 10)
        self.create_subscription(Pose2D, robot_pose_topic, self.robot_pose_cb, 10)
        self.create_subscription(String, robot_status_topic, self.robot_status_cb, 10)
        self.create_subscription(Pose2D, goal_pose_topic, self.goal_pose_cb, 10)
        self.create_subscription(String, next_place_topic, self.next_place_cb, 10)
        self.create_subscription(String, follow_state_topic, self.follow_state_cb, 10)
        self.create_subscription(Bool, auth_ready_topic, self.auth_ready_cb, 10)
        self.create_subscription(String, patrol_command_topic, self.patrol_command_cb, 10)

        self.get_logger().info("Robot GUI ROS node started")
        self.get_logger().info(f"camera={annotated_topic}")
        self.get_logger().info(f"robot_pose={robot_pose_topic}, robot_status={robot_status_topic}")
        self.get_logger().info(f"goal_pose={goal_pose_topic}, next_place={next_place_topic}")
        self.get_logger().info(f"follow_state={follow_state_topic}, auth_ready={auth_ready_topic}")
        self.get_logger().info(f"patrol_command={patrol_command_topic}")

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


# ==========================================================
# PyQt GUI
# ==========================================================
class SecurityRobotGui(QWidget):
    def __init__(self, state: GuiState):
        super().__init__()
        self.state = state

        self.setWindowTitle("Security Patrol Robot GUI")
        self.resize(1100, 780)

        # Camera
        self.camera_label = QLabel("Waiting for /person_tracking/annotated ...")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumHeight(480)
        self.camera_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.camera_label.setStyleSheet(
            "background-color: #111; color: #ddd; border-radius: 8px; padding: 8px;"
        )

        # Status labels
        self.robot_pose_label = QLabel()
        self.robot_status_label = QLabel()
        self.goal_pose_label = QLabel()
        self.next_place_label = QLabel()
        self.follow_state_label = QLabel()
        self.auth_state_label = QLabel()
        self.command_label = QLabel()

        for label in [
            self.robot_pose_label,
            self.robot_status_label,
            self.goal_pose_label,
            self.next_place_label,
            self.follow_state_label,
            self.auth_state_label,
            self.command_label,
        ]:
            label.setFont(QFont("DejaVu Sans", 12))
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self._build_layout()

        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.refresh_ui)
        self.ui_timer.start(100)  # 10 Hz GUI refresh

    def _build_layout(self):
        root = QVBoxLayout()
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        title = QLabel("Indoor Security Patrol Robot")
        title.setFont(QFont("DejaVu Sans", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        root.addWidget(title)

        root.addWidget(self.camera_label, stretch=5)

        bottom = QHBoxLayout()
        bottom.setSpacing(10)

        robot_box = QGroupBox("Robot State")
        robot_layout = QVBoxLayout()
        robot_layout.addWidget(self.robot_pose_label)
        robot_layout.addWidget(self.robot_status_label)
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
        perception_box.setLayout(perception_layout)

        bottom.addWidget(robot_box, stretch=1)
        bottom.addWidget(goal_box, stretch=1)
        bottom.addWidget(perception_box, stretch=1)

        root.addLayout(bottom, stretch=2)
        self.setLayout(root)

    @staticmethod
    def fmt_pose(x: Optional[float], y: Optional[float], yaw: Optional[float]) -> str:
        if x is None or y is None or yaw is None:
            return "x: - | y: - | yaw: -"
        return f"x: {x:.3f} | y: {y:.3f} | yaw: {yaw:.3f}"

    @staticmethod
    def compute_auth_text(follow_state: str, auth_ready: bool) -> str:
        # Uses only currently published values.
        # It cannot distinguish success/fail/timeout without a dedicated /auth_status topic.
        normalized = (follow_state or "").strip().upper()

        if normalized == "TRACKING" and auth_ready:
            return "RFID 대기"
        if normalized == "TRACKING" and not auth_ready:
            return "인증 대기 아님"
        return "idle"

    def refresh_ui(self):
        self.refresh_camera()

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
