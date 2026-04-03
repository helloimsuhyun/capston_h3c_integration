# webrtc_sender.py
import asyncio
import threading
from typing import Optional

import cv2
import numpy as np
from av import VideoFrame
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
import requests


class BufferVideoTrack(VideoStreamTrack):
    def __init__(self, buffer):
        super().__init__()
        self.buffer = buffer
        self._last_frame: Optional[np.ndarray] = None

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        try:
            rgb = await asyncio.to_thread(self.buffer.wait_new, 1.0)
            self._last_frame = rgb
        except Exception:
            rgb = self._last_frame

        if rgb is None:
            rgb = np.zeros((720, 1280, 3), dtype=np.uint8)

        rgb = cv2.resize(rgb, (1280, 720), interpolation=cv2.INTER_AREA)

        frame = VideoFrame.from_ndarray(rgb, format="rgb24")
        frame.pts = pts
        frame.time_base = time_base
        return frame


class WebRTCSender:
    def __init__(self, buffer, signaling_base_url: str):
        self.buffer = buffer
        self.signaling_base_url = signaling_base_url.rstrip("/")
        self.thread: Optional[threading.Thread] = None
        self.running = False
        self.pc: Optional[RTCPeerConnection] = None

    def start(self):
        print("[WebRTC] start() called")
        print("[WebRTC] signaling_base_url =", self.signaling_base_url)

        if self.thread is not None and self.thread.is_alive():
            print("[WebRTC] thread already alive")
            return

        self.running = True
        self.thread = threading.Thread(target=self._thread_main, daemon=True)
        self.thread.start()
        print("[WebRTC] thread started")

    def stop(self):
        print("[WebRTC] stop() called")
        self.running = False

    def _thread_main(self):
        print("[WebRTC] _thread_main entered")
        try:
            asyncio.run(self._run())
        except Exception as e:
            print("[WebRTC] _thread_main fatal error:", repr(e))

    async def _run(self):
        print("[WebRTC] _run loop started")

        while self.running:
            try:
                poll_url = f"{self.signaling_base_url}/sender_poll"
                print("[WebRTC] polling:", poll_url)

                resp = requests.get(poll_url, timeout=35.0)
                print("[WebRTC] sender_poll status =", resp.status_code)

                if resp.status_code != 200:
                    await asyncio.sleep(1.0)
                    continue

                offer_data = resp.json()
                print("[WebRTC] offer received")
                print("[WebRTC] offer keys =", list(offer_data.keys()))

                pc = RTCPeerConnection()
                self.pc = pc
                print("[WebRTC] RTCPeerConnection created")

                @pc.on("connectionstatechange")
                async def on_connectionstatechange():
                    print("[WebRTC] sender state:", pc.connectionState)

                pc.addTrack(BufferVideoTrack(self.buffer))
                print("[WebRTC] track added")

                offer = RTCSessionDescription(
                    sdp=offer_data["sdp"],
                    type=offer_data["type"],
                )

                await pc.setRemoteDescription(offer)
                print("[WebRTC] remote description set")

                answer = await pc.createAnswer()
                print("[WebRTC] answer created")

                await pc.setLocalDescription(answer)
                print("[WebRTC] local description set")

                ans_url = f"{self.signaling_base_url}/sender_answer"
                r = requests.post(
                    ans_url,
                    json={
                        "sdp": pc.localDescription.sdp,
                        "type": pc.localDescription.type,
                    },
                    timeout=10.0,
                )
                print("[WebRTC] sender_answer post status =", r.status_code)

                while self.running and pc.connectionState not in ("failed", "closed", "disconnected"):
                    await asyncio.sleep(1.0)

            except Exception as e:
                print("[WebRTC] sender error:", repr(e))
            finally:
                if self.pc is not None:
                    try:
                        await self.pc.close()
                        print("[WebRTC] pc closed")
                    except Exception as e:
                        print("[WebRTC] pc close error:", repr(e))
                    self.pc = None

            await asyncio.sleep(1.0)