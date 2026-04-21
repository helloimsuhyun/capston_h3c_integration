#!/usr/bin/env python3
import json
import time
from datetime import datetime
from threading import Lock
from typing import Optional

import cv2
import requests

import rclpy
from rclpy.node import Node

from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from std_msgs.msg import Bool, String

try:
    from smartcard.System import readers as pcsc_readers
    from smartcard.Exceptions import CardConnectionException, NoCardException
    SMARTCARD_AVAILABLE = True
    SMARTCARD_IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover
    SMARTCARD_AVAILABLE = False
    SMARTCARD_IMPORT_ERROR = exc
    pcsc_readers = None
    CardConnectionException = Exception
    NoCardException = Exception


class SecondaryAuthNode(Node):
    """RFID/NFC based secondary authentication bridge.

    Flow:
      1) subscribe latest follow person id
      2) subscribe latest annotated frame
      3) when auth_ready rises, call /auth/start and snapshot image
      4) wait RFID UID from ACR122U compatible PC/SC reader
      5) call /auth/rfid on UID or /auth/timeout on timeout
      6) publish auth state/result for downstream robot UI logic
    """

    IDLE = 'IDLE'
    WAITING_RFID = 'WAITING_RFID'
    SUCCESS = 'SUCCESS'
    FAIL = 'FAIL'
    TIMEOUT = 'TIMEOUT'
    ERROR = 'ERROR'

    def __init__(self):
        super().__init__('secondary_auth_node')

        # HTTP / ROS parameters
        #self.declare_parameter('server_base_url', 'http://127.0.0.1:8000')     #테스트용 주소
        self.declare_parameter('server_base_url', 'http://192.168.0.16:8000')
        self.declare_parameter('follow_person_id_topic', '/person_tracking/follow_person_id')
        self.declare_parameter('annotated_topic', '/person_tracking/annotated')
        self.declare_parameter('auth_ready_topic', '/auth_ready')
        self.declare_parameter('result_topic', '/auth/result_json')
        self.declare_parameter('state_topic', '/auth/state')

        # reader / timer params
        self.declare_parameter('reader_name_hint', 'ACR122')
        self.declare_parameter('auth_timeout_sec', 10.0)
        self.declare_parameter('poll_period_sec', 0.25)
        self.declare_parameter('request_timeout_sec', 5.0)
        self.declare_parameter('jpeg_quality', 90)
        self.declare_parameter('rfid_read_cooldown_sec', 1.5)
        self.declare_parameter('timeout_retry_sec', 1.0)

        self.server_base_url = str(self.get_parameter('server_base_url').value).rstrip('/')
        self.follow_person_id_topic = str(self.get_parameter('follow_person_id_topic').value)
        self.annotated_topic = str(self.get_parameter('annotated_topic').value)
        self.auth_ready_topic = str(self.get_parameter('auth_ready_topic').value)
        self.result_topic = str(self.get_parameter('result_topic').value)
        self.state_topic = str(self.get_parameter('state_topic').value)
        self.reader_name_hint = str(self.get_parameter('reader_name_hint').value)
        self.auth_timeout_sec = float(self.get_parameter('auth_timeout_sec').value)
        self.poll_period_sec = float(self.get_parameter('poll_period_sec').value)
        self.request_timeout_sec = float(self.get_parameter('request_timeout_sec').value)
        self.jpeg_quality = int(self.get_parameter('jpeg_quality').value)
        self.rfid_read_cooldown_sec = float(self.get_parameter('rfid_read_cooldown_sec').value)
        self.timeout_retry_sec = float(self.get_parameter('timeout_retry_sec').value)

        self.bridge = CvBridge()
        self.lock = Lock()
        self.session = requests.Session()

        # subscribed latest values
        self.latest_follow_person_id: str = ''
        self.latest_auth_frame = None
        self.auth_start_frame = None

        # auth session state
        self.auth_event_id: Optional[str] = None
        self.auth_in_progress = False
        self.auth_started_mono = 0.0
        self.last_auth_ready = False
        self.last_uid: Optional[str] = None
        self.last_uid_read_mono = 0.0
        self.last_timeout_attempt_mono = 0.0
        self.state = self.IDLE

        # pubs/subs/timer
        self.follow_sub = self.create_subscription(
            String, self.follow_person_id_topic, self.follow_person_id_cb, 10)
        self.annotated_sub = self.create_subscription(
            Image, self.annotated_topic, self.annotated_cb, 10)
        self.auth_ready_sub = self.create_subscription(
            Bool, self.auth_ready_topic, self.auth_ready_cb, 10)

        self.state_pub = self.create_publisher(String, self.state_topic, 10)
        self.result_pub = self.create_publisher(String, self.result_topic, 10)
        self.timer = self.create_timer(self.poll_period_sec, self.poll_loop)

        if not SMARTCARD_AVAILABLE:
            self.get_logger().error(
                f'pyscard import failed: {SMARTCARD_IMPORT_ERROR}. '
                'Install PC/SC stack and pyscard before using RFID auth.'
            )

        self.publish_state(self.IDLE)
        self.get_logger().info(
            'SecondaryAuthNode started | '
            f'server={self.server_base_url} | '
            f'follow_person_id_topic={self.follow_person_id_topic} | '
            f'annotated_topic={self.annotated_topic} | '
            f'auth_ready_topic={self.auth_ready_topic} | '
            f'reader_hint={self.reader_name_hint}'
        )

    # ---------- ROS callbacks ----------
    def follow_person_id_cb(self, msg: String):
        with self.lock:
            self.latest_follow_person_id = msg.data.strip()

    def annotated_cb(self, msg: Image):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as exc:
            self.get_logger().warn(f'annotated image convert failed: {exc}')
            return

        with self.lock:
            self.latest_auth_frame = frame.copy()

    def auth_ready_cb(self, msg: Bool):
        if msg.data and not self.last_auth_ready:
            self.start_auth()
        self.last_auth_ready = bool(msg.data)

    # ---------- auth session ----------
    def start_auth(self):
        with self.lock:
            if self.auth_in_progress:
                self.get_logger().warn('auth already in progress; ignore new start trigger')
                return

            tracking_person_id = self.latest_follow_person_id
            frame_snapshot = None if self.latest_auth_frame is None else self.latest_auth_frame.copy()

        if not tracking_person_id:
            self.get_logger().warn('auth_ready received but latest follow_person_id is empty')
            return

        payload = {
            'tracking_person_id': tracking_person_id,
        }

        try:
            resp = self.session.post(
                f'{self.server_base_url}/auth/start',
                json=payload,
                timeout=self.request_timeout_sec,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            self.publish_state(self.ERROR)
            self.get_logger().error(f'/auth/start failed: {exc}')
            return

        if not data.get('ok', False):
            self.publish_state(self.ERROR)
            self.get_logger().error(f'/auth/start response not ok: {data}')
            return

        auth_event_id = data.get('auth_event_id')
        if not auth_event_id:
            self.publish_state(self.ERROR)
            self.get_logger().error(f'/auth/start response missing auth_event_id: {data}')
            return

        with self.lock:
            self.auth_event_id = str(auth_event_id)
            self.auth_start_frame = frame_snapshot
            self.auth_in_progress = True
            self.auth_started_mono = time.monotonic()
            self.last_uid = None
            self.last_uid_read_mono = 0.0
            self.last_timeout_attempt_mono = 0.0

        self.publish_state(self.WAITING_RFID)
        self.get_logger().info(
            f'auth started | tracking_person_id={tracking_person_id} | auth_event_id={auth_event_id}'
        )

    def poll_loop(self):
        with self.lock:
            in_progress = self.auth_in_progress
            started_mono = self.auth_started_mono

        if not in_progress:
            return

        elapsed = time.monotonic() - started_mono
        if elapsed >= self.auth_timeout_sec:
            now = time.monotonic()
            if (now - self.last_timeout_attempt_mono) >= self.timeout_retry_sec:
                self.last_timeout_attempt_mono = now
                self.send_timeout()
            return

        uid = self.read_uid_once()
        if uid is None:
            return

        now = time.monotonic()
        if self.last_uid == uid and (now - self.last_uid_read_mono) < self.rfid_read_cooldown_sec:
            return

        self.last_uid = uid
        self.last_uid_read_mono = now
        self.send_rfid(uid)

    # ---------- PC/SC reader ----------
    def select_reader(self):
        if not SMARTCARD_AVAILABLE or pcsc_readers is None:
            return None

        available = pcsc_readers()
        if not available:
            return None

        hint = self.reader_name_hint.lower().strip()
        if hint:
            for reader in available:
                if hint in str(reader).lower():
                    return reader

        return available[0]

    def read_uid_once(self) -> Optional[str]:
        reader = None
        try:
            reader = self.select_reader()
        except Exception as exc:
            self.get_logger().warn(f'failed to enumerate NFC readers: {exc}')
            return None

        if reader is None:
            return None

        conn = None
        try:
            conn = reader.createConnection()
            conn.connect()
            data, sw1, sw2 = conn.transmit([0xFF, 0xCA, 0x00, 0x00, 0x00])
            if sw1 == 0x90 and sw2 == 0x00 and data:
                return ''.join(f'{byte:02X}' for byte in data)
            return None
        except NoCardException:
            return None
        except CardConnectionException:
            return None
        except Exception as exc:
            self.get_logger().warn(f'NFC read failed: {exc}')
            return None
        finally:
            if conn is not None:
                try:
                    conn.disconnect()
                except Exception:
                    pass

    # ---------- server calls ----------
    def send_rfid(self, uid: str):
        with self.lock:
            auth_event_id = self.auth_event_id
            frame = None if self.auth_start_frame is None else self.auth_start_frame.copy()

        if not auth_event_id:
            self.get_logger().warn('send_rfid skipped: auth_event_id is empty')
            return

        data = {
            'auth_event_id': auth_event_id,
            'rfid_uid': uid,
        }
        files = self.build_image_files(frame)

        try:
            resp = self.session.post(
                f'{self.server_base_url}/auth/rfid',
                data=data,
                files=files,
                timeout=self.request_timeout_sec,
            )
            resp.raise_for_status()
            result = resp.json()
        except Exception as exc:
            self.get_logger().error(f'/auth/rfid failed: {exc}')
            return

        auth_event = result.get('auth_event', {}) if isinstance(result, dict) else {}
        status = str(auth_event.get('status', '')).lower()
        if status == 'success':
            self.publish_state(self.SUCCESS)
        elif status == 'fail':
            self.publish_state(self.FAIL)
        else:
            self.publish_state(self.ERROR)

        self.publish_result(result)
        self.get_logger().info(f'/auth/rfid result: {result}')
        self.clear_auth_state()

    def send_timeout(self):
        with self.lock:
            auth_event_id = self.auth_event_id
            frame = None if self.auth_start_frame is None else self.auth_start_frame.copy()

        if not auth_event_id:
            self.get_logger().warn('send_timeout skipped: auth_event_id is empty')
            return

        data = {
            'auth_event_id': auth_event_id,
            'timestamp': datetime.now().isoformat(),
        }
        files = self.build_image_files(frame)

        try:
            resp = self.session.post(
                f'{self.server_base_url}/auth/timeout',
                data=data,
                files=files,
                timeout=self.request_timeout_sec,
            )
            resp.raise_for_status()
            result = resp.json()
        except Exception as exc:
            self.get_logger().error(f'/auth/timeout failed: {exc}')
            return

        self.publish_state(self.TIMEOUT)
        self.publish_result(result)
        self.get_logger().info(f'/auth/timeout result: {result}')
        self.clear_auth_state()

    # ---------- helpers ----------
    def build_image_files(self, frame):
        if frame is None:
            return None

        ok, encoded = cv2.imencode(
            '.jpg', frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality]
        )
        if not ok:
            self.get_logger().warn('image encoding failed; sending request without image')
            return None

        return {
            'image': ('auth.jpg', encoded.tobytes(), 'image/jpeg')
        }

    def publish_result(self, payload):
        msg = String()
        try:
            msg.data = json.dumps(payload, ensure_ascii=False)
        except Exception:
            msg.data = str(payload)
        self.result_pub.publish(msg)

    def publish_state(self, state: str):
        self.state = state
        msg = String()
        msg.data = state
        self.state_pub.publish(msg)

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
