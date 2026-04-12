#!/usr/bin/env python3
from __future__ import annotations

import threading

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from fastapi.middleware.cors import CORSMiddleware


class PlaceReq(BaseModel):
    place_id: str


class PatrolHttpBridge(Node):

    def __init__(self):
        super().__init__("patrol_http_bridge")

        self.trigger_pub = self.create_publisher(
            String,
            "/patrol/capture_trigger",
            10
        )

        self.app = FastAPI()

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @self.app.get("/health")
        def health():
            return {"ok": True}

        @self.app.post("/patrol/capture")
        def trigger_capture(req: PlaceReq):
            place_id = str(req.place_id).strip()
            if not place_id:
                return {"ok": False, "error": "place_id is required"}

            msg = String()
            msg.data = place_id
            self.trigger_pub.publish(msg)

            self.get_logger().info(f"capture trigger -> {msg.data}")
            return {"ok": True, "place_id": msg.data}
        
        @self.app.post("/patrol/place_and_capture")
        def place_and_capture(req: PlaceReq):
            place_id = str(req.place_id).strip()
            if not place_id:
                return {"ok": False, "error": "place_id is required"}
            msg = String()
            msg.data = place_id
            self.trigger_pub.publish(msg)

            self.get_logger().info(f"place -> {msg.data}, capture trigger")
            return {"ok": True, "place_id": msg.data}

    def run_http(self, host="0.0.0.0", port=8090):
        uvicorn.run(self.app, host=host, port=port, log_level="info")


def main():
    rclpy.init()

    node = PatrolHttpBridge()

    t = threading.Thread(
        target=node.run_http,
        kwargs={"host": "0.0.0.0", "port": 8090},
        daemon=True
    )
    t.start()

    node.get_logger().info("HTTP bridge ready at :8090")
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()