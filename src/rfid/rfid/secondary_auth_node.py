#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import subprocess
from datetime import datetime
from threading import Lock
from typing import Optional

import cv2
import requests
import rclpy
from rclpy.node import Node

from std_msgs.msg import String, Bool
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

from smartcard.System import readers
from smartcard.Exceptions import CardConnectionException, NoCardException


class SecondaryAuthNode(Node):
    def __init__(self):
        super().__init__('secondary_auth_node')

        # =========================
        # 사용자 설정
        # =========================
        self.server_base_url = 'http://192.168.0.16:8000'

        self.follow_person_id_topic = '/person_tracking/follow_person_id'
        self.annotated_topic = '/person_tracking/annotated'
        self.auth_ready_topic = '/auth_ready'

        self.reader_name_hint = 'ACR122'
        self.auth_timeout_sec = 10.0
        self.poll_period_sec = 0.2
        self.request_timeout_sec = 5.0
        self.jpeg_quality = 90
        self.rfid_read_cooldown_sec = 1.5

        # =========================
        # 내부 상태
        # =========================
        self.bridge = CvBridge()
        self.lock = Lock()
        self.http = requests.Session()

        self.latest_follow_person_id: str = ""
        self.latest_auth_frame = None
        self.auth_start_frame = None

        self.auth_in_progress: bool = False
        self.auth_event_id: Optional[str] = None
        self.auth_started_mono: float = 0.0

        self.last_auth_ready: bool = False
        self.last_uid: Optional[str] = None
        self.last_uid_read_ts: float = 0.0

        # =========================
        # ROS 인터페이스
        # =========================
        self.create_subscription(
            String,
            self.follow_person_id_topic,
            self.follow_person_id_cb,
            10
        )

        self.create_subscription(
            Image,
            self.annotated_topic,
            self.annotated_cb,
            10
        )

        self.create_subscription(
            Bool,
            self.auth_ready_topic,
            self.auth_ready_cb,
            10
        )

        # PC/SC 워밍업
        self.warmup_pcsc()

        self.timer = self.create_timer(self.poll_period_sec, self.poll_loop)

        self.get_logger().info(
            f'SecondaryAuthNode started | '
            f'server={self.server_base_url} | '
            f'follow_person_id_topic={self.follow_person_id_topic} | '
            f'annotated_topic={self.annotated_topic} | '
            f'auth_ready_topic={self.auth_ready_topic} | '
            f'reader_hint={self.reader_name_hint}'
        )

    # =========================
    # PC/SC 워밍업
    # =========================
    def warmup_pcsc(self):
        self.get_logger().info('warming up pcsc with pcsc_scan...')

        try:
            subprocess.run(
                ['bash', '-lc', 'timeout 2s pcsc_scan >/dev/null 2>&1 || true'],
                check=False
            )
            self.get_logger().info('pcsc warmup done')
        except Exception as e:
            self.get_logger().warn(f'pcsc warmup failed: {e}')

    # =========================
    # ROS callbacks
    # =========================
    def follow_person_id_cb(self, msg: String):
        new_id = msg.data.strip()

        if new_id == "":
            return

        with self.lock:
            self.latest_follow_person_id = new_id

    def annotated_cb(self, msg: Image):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().warn(f'annotated image convert failed: {e}')
            return

        with self.lock:
            self.latest_auth_frame = frame.copy()

    def auth_ready_cb(self, msg: Bool):
        if msg.data and not self.last_auth_ready:
            self.start_auth()

        self.last_auth_ready = msg.data

    # =========================
    # 인증 시작
    # =========================
    def start_auth(self):
        with self.lock:
            if self.auth_in_progress:
                self.get_logger().warn('auth already in progress')
                return

            tracking_person_id = self.latest_follow_person_id
            frame_snapshot = None if self.latest_auth_frame is None else self.latest_auth_frame.copy()

        if tracking_person_id == "":
            self.get_logger().warn('latest_follow_person_id is empty')
            return

        payload = {
            "tracking_person_id": tracking_person_id,
        }

        try:
            resp = self.http.post(
                f'{self.server_base_url}/auth/start',
                json=payload,
                timeout=self.request_timeout_sec
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            self.get_logger().error(f'/auth/start failed: {e}')
            return

        if not data.get("ok", False):
            self.get_logger().error(f'/auth/start response not ok: {data}')
            return

        auth_event_id = data.get("auth_event_id")
        if not auth_event_id:
            self.get_logger().error(f'no auth_event_id in response: {data}')
            return

        with self.lock:
            self.auth_in_progress = True
            self.auth_event_id = auth_event_id
            self.auth_start_frame = frame_snapshot
            self.auth_started_mono = time.monotonic()

        self.get_logger().info(
            f'auth started | tracking_person_id={tracking_person_id} | auth_event_id={auth_event_id}'
        )

    # =========================
    # 주기 루프
    # =========================
    def poll_loop(self):
        with self.lock:
            in_progress = self.auth_in_progress
            started_mono = self.auth_started_mono

        if not in_progress:
            return

        if time.monotonic() - started_mono >= self.auth_timeout_sec:
            self.send_timeout()
            return

        uid = self.read_uid_once()
        if uid is None:
            return

        now = time.monotonic()
        if self.last_uid == uid and (now - self.last_uid_read_ts) < self.rfid_read_cooldown_sec:
            return

        self.last_uid = uid
        self.last_uid_read_ts = now

        self.send_rfid(uid)

    # =========================
    # ACR122U UID 읽기
    # =========================
    def select_reader(self):
        hint = self.reader_name_hint.lower()

        for _ in range(10):
            try:
                available = readers()
                if available:
                    for r in available:
                        if hint in str(r).lower():
                            return r
                    return available[0]
            except Exception as e:
                self.get_logger().warn(f'reader enumeration failed: {e}')

            time.sleep(0.5)

        return None

    def read_uid_once(self) -> Optional[str]:
        reader = self.select_reader()

        if reader is None:
            return None

        conn = None
        try:
            conn = reader.createConnection()
            conn.connect()

            apdu = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, sw1, sw2 = conn.transmit(apdu)

            if sw1 == 0x90 and sw2 == 0x00 and len(data) > 0:
                uid = ''.join(f'{b:02X}' for b in data)
                return uid

            return None

        except NoCardException:
            return None
        except CardConnectionException:
            return None
        except Exception as e:
            self.get_logger().warn(f'UID read failed: {e}')
            return None
        finally:
            if conn is not None:
                try:
                    conn.disconnect()
                except Exception:
                    pass

    # =========================
    # 서버 전송
    # =========================
    def send_rfid(self, uid: str):
        with self.lock:
            auth_event_id = self.auth_event_id
            frame = None if self.auth_start_frame is None else self.auth_start_frame.copy()

        if not auth_event_id:
            self.get_logger().warn('send_rfid called but auth_event_id is empty')
            return

        data = {
            "auth_event_id": auth_event_id,
            "rfid_uid": uid,
        }

        files = self.build_image_file(frame)

        try:
            resp = self.http.post(
                f'{self.server_base_url}/auth/rfid',
                data=data,
                files=files,
                timeout=self.request_timeout_sec
            )
            resp.raise_for_status()
            result = resp.json()
        except Exception as e:
            self.get_logger().error(f'/auth/rfid failed: {e}')
            return

        self.get_logger().info(f'/auth/rfid result: {result}')
        self.clear_auth_state()

    def send_timeout(self):
        with self.lock:
            auth_event_id = self.auth_event_id
            frame = None if self.auth_start_frame is None else self.auth_start_frame.copy()

        if not auth_event_id:
            self.get_logger().warn('send_timeout called but auth_event_id is empty')
            return

        data = {
            "auth_event_id": auth_event_id,
            "timestamp": datetime.now().isoformat(),
        }

        files = self.build_image_file(frame)

        try:
            resp = self.http.post(
                f'{self.server_base_url}/auth/timeout',
                data=data,
                files=files,
                timeout=self.request_timeout_sec
            )
            resp.raise_for_status()
            result = resp.json()
        except Exception as e:
            self.get_logger().error(f'/auth/timeout failed: {e}')
            return

        self.get_logger().info(f'/auth/timeout result: {result}')
        self.clear_auth_state()

    # =========================
    # 이미지 첨부
    # =========================
    def build_image_file(self, frame):
        if frame is None:
            return None

        ok, enc = cv2.imencode(
            '.jpg',
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality]
        )
        if not ok:
            self.get_logger().warn('image encoding failed')
            return None

        return {
            'image': ('auth.jpg', enc.tobytes(), 'image/jpeg')
        }

    # =========================
    # 상태 초기화
    # =========================
    def clear_auth_state(self):
        with self.lock:
            self.auth_in_progress = False
            self.auth_event_id = None
            self.auth_start_frame = None
            self.auth_started_mono = 0.0
            self.last_auth_ready = False

        self.get_logger().info('auth session cleared')


def main(args=None):
    rclpy.init(args=args)
    node = SecondaryAuthNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
