"""
/sound/upload_enable
/sound/allowed_labels
오디오 전송 노드에서 위 토픽을 SUB하여 필터링할 라벨, 구역별 ON/OFF를 결정

"""

import json
import threading
from typing import List, Dict, Any, Optional, Tuple

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool, String
from geometry_msgs.msg import Pose2D


class AudioRegion(BaseModel):
    region_id: Optional[int] = None
    name: str
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    is_enabled: bool = True


class AudioConfigReq(BaseModel):
    audio_mode: int = Field(..., description="0: OFF, 1: ALWAYS, 2: REGION")
    run_audio_upload: bool
    regions: List[AudioRegion] = Field(default_factory=list)
    allowed_labels: List[str] = Field(default_factory=list)
    updated_at: Optional[str] = None


class AudioUploadControlNode(Node):
    def __init__(self):
        super().__init__("audio_upload_control_node")

        # ROS topics
        self.declare_parameter("robot_pose_topic", "/robot_pose")
        self.declare_parameter("upload_enable_topic", "/sound/upload_enable")
        self.declare_parameter("allowed_labels_topic", "/sound/allowed_labels")

        # local HTTP server
        self.declare_parameter("notify_host", "0.0.0.0")
        self.declare_parameter("notify_port", 8091)

        # behavior
        self.declare_parameter("log_region_match", True)
        self.declare_parameter("start_enabled", False)

        self.robot_pose_topic = str(self.get_parameter("robot_pose_topic").value)
        self.upload_enable_topic = str(self.get_parameter("upload_enable_topic").value)
        self.allowed_labels_topic = str(self.get_parameter("allowed_labels_topic").value)

        self.notify_host = str(self.get_parameter("notify_host").value)
        self.notify_port = int(self.get_parameter("notify_port").value)

        self.log_region_match = bool(self.get_parameter("log_region_match").value)
        self.start_enabled = bool(self.get_parameter("start_enabled").value)

        self.lock = threading.Lock()

        # current pose
        self.current_pose: Optional[Pose2D] = None

        # pushed config cache
        self.audio_mode = 2
        self.run_audio_upload_hint = True
        self.enabled_regions: List[Dict[str, Any]] = []
        self.allowed_labels: List[str] = []
        self.last_config_ok = False
        self.last_config_updated_at: Optional[str] = None

        # output state
        self.last_enable: Optional[bool] = None
        self.last_labels_json: Optional[str] = None
        self.last_region_name: Optional[str] = None

        self.pose_sub = self.create_subscription(
            Pose2D,
            self.robot_pose_topic,
            self.pose_callback,
            10,
        )

        self.upload_enable_pub = self.create_publisher(
            Bool,
            self.upload_enable_topic,
            10,
        )

        self.allowed_labels_pub = self.create_publisher(
            String,
            self.allowed_labels_topic,
            10,
        )

        self.eval_timer = self.create_timer(0.2, self.evaluate_upload_enable)

        self.app = FastAPI()
        self._setup_routes()

        self.http_thread = threading.Thread(
            target=self._run_http_server,
            daemon=True,
        )
        self.http_thread.start()

        self.evaluate_upload_enable()
        self.publish_allowed_labels(force=True)

        self.get_logger().info(
            f"[INIT] AudioUploadControlNode | "
            f"robot_pose={self.robot_pose_topic} | "
            f"upload_enable_topic={self.upload_enable_topic} | "
            f"allowed_labels_topic={self.allowed_labels_topic} | "
            f"http={self.notify_host}:{self.notify_port} | "
            f"start_enabled={self.start_enabled}"
        )

    # =========================
    # HTTP
    # =========================

    def _setup_routes(self):
        node = self

        @self.app.post("/robot/audio_config")
        async def post_audio_config(req: AudioConfigReq):
            if req.audio_mode not in (0, 1, 2):
                raise HTTPException(status_code=400, detail="invalid audio_mode")

            normalized_regions: List[Dict[str, Any]] = []

            for r in req.regions:
                x1 = min(float(r.x_min), float(r.x_max))
                x2 = max(float(r.x_min), float(r.x_max))
                y1 = min(float(r.y_min), float(r.y_max))
                y2 = max(float(r.y_min), float(r.y_max))

                normalized_regions.append({
                    "region_id": r.region_id,
                    "name": r.name,
                    "x_min": x1,
                    "x_max": x2,
                    "y_min": y1,
                    "y_max": y2,
                    "is_enabled": bool(r.is_enabled),
                })

            labels = [
                str(x).strip()
                for x in req.allowed_labels
                if str(x).strip()
            ]
            labels = sorted(set(labels))

            with node.lock:
                node.audio_mode = int(req.audio_mode)
                node.run_audio_upload_hint = bool(req.run_audio_upload)
                node.enabled_regions = normalized_regions
                node.allowed_labels = labels
                node.last_config_ok = True
                node.last_config_updated_at = req.updated_at

            node.get_logger().info(
                f"[AUDIO CONFIG] mode={req.audio_mode} "
                f"run_audio_upload={req.run_audio_upload} "
                f"regions={len(normalized_regions)} "
                f"allowed_labels={labels} "
                f"updated_at={req.updated_at}"
            )

            node.evaluate_upload_enable()
            node.publish_allowed_labels(force=True)

            return {
                "ok": True,
                "applied": True,
                "cached_mode": node.audio_mode,
                "run_audio_upload": node.run_audio_upload_hint,
                "cached_region_count": len(normalized_regions),
                "allowed_labels": labels,
            }

        @self.app.get("/health")
        async def health():
            return {"ok": True}

    def _run_http_server(self):
        uvicorn.run(
            self.app,
            host=self.notify_host,
            port=self.notify_port,
            log_level="info",
        )

    # =========================
    # ROS callbacks
    # =========================

    def pose_callback(self, msg: Pose2D):
        with self.lock:
            self.current_pose = msg

    # =========================
    # Region logic
    # =========================

    def point_in_region(self, x: float, y: float, region: Dict[str, Any]) -> bool:
        try:
            x_min = float(region["x_min"])
            x_max = float(region["x_max"])
            y_min = float(region["y_min"])
            y_max = float(region["y_max"])
        except Exception:
            return False

        return (x_min <= x <= x_max) and (y_min <= y <= y_max)

    def find_matching_region(self, x: float, y: float) -> Optional[Dict[str, Any]]:
        with self.lock:
            regions = list(self.enabled_regions)

        for region in regions:
            if not bool(region.get("is_enabled", True)):
                continue

            if self.point_in_region(x, y, region):
                return region

        return None

    # =========================
    # Upload enable logic
    # =========================

    def compute_upload_enable(self) -> Tuple[bool, Optional[str], str]:
        with self.lock:
            pose = self.current_pose
            audio_mode = self.audio_mode
            run_audio_upload_hint = self.run_audio_upload_hint
            config_ok = self.last_config_ok

        if not config_ok:
            if self.start_enabled:
                return True, None, "startup_mode_always"
            return False, None, "startup_mode_off"

        if audio_mode == 0:
            return False, None, "mode_off"

        if audio_mode == 1:
            return True, None, "mode_always"

        if audio_mode == 2:
            if not run_audio_upload_hint:
                return False, None, "mode_region_no_active_region"

            if pose is None:
                return False, None, "no_robot_pose"

            x = float(pose.x)
            y = float(pose.y)

            region = self.find_matching_region(x, y)
            if region is None:
                return False, None, "outside_all_regions"

            region_name = str(
                region.get("name", f"region_{region.get('region_id', 'unknown')}")
            )
            return True, region_name, "inside_enabled_region"

        return False, None, "unknown_mode"

    def evaluate_upload_enable(self):
        enable, region_name, reason = self.compute_upload_enable()

        if self.last_enable is None or self.last_enable != enable:
            self.publish_upload_enable(enable, reason)

        if self.log_region_match and enable and region_name != self.last_region_name:
            self.last_region_name = region_name
            if region_name is not None:
                self.get_logger().info(f"[AUDIO REGION] matched: {region_name}")

        if not enable:
            self.last_region_name = None

    def publish_upload_enable(self, enable: bool, reason: str = ""):
        msg = Bool()
        msg.data = bool(enable)
        self.upload_enable_pub.publish(msg)

        self.last_enable = bool(enable)
        self.get_logger().info(f"[AUDIO UPLOAD ENABLE] {enable} reason={reason}")

    def publish_allowed_labels(self, force: bool = False):
        with self.lock:
            labels = list(self.allowed_labels)

        labels_json = json.dumps(labels, ensure_ascii=False)

        if not force and self.last_labels_json == labels_json:
            return

        msg = String()
        msg.data = labels_json
        self.allowed_labels_pub.publish(msg)

        self.last_labels_json = labels_json
        self.get_logger().info(f"[AUDIO ALLOWED LABELS] {labels_json}")


def main(args=None):
    rclpy.init(args=args)
    node = AudioUploadControlNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()