import argparse
import json
import time
import logging
import tempfile
import subprocess
from pathlib import Path
import threading

import aiohttp
from pytapo import Tapo
from yarl import URL

from unifi.cams.base import UnifiCamBase
from typing import Any

AVClientRequest = AVClientResponse = dict[str, Any]

class TapoCam(UnifiCamBase):
    def __init__(self, args: argparse.Namespace, logger: logging.Logger) -> None:
        super().__init__(args, logger)
        self.snapshot_dir: str = tempfile.mkdtemp()
        self.cam = Tapo(args.ip, args.username, args.password)
        self.snapshot_stream = None
        self.username = args.username
        self.password = args.password
        self.isMoving = False # is this needed?
        self.ip = args.ip
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        print(self.cam.getBasicInfo())
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

        self.stream_source = dict()
        self.stream_source["video1"] = (f"rtsp://{args.username}:{args.password}@{args.ip}:554/stream1")
        self.stream_source["video2"] = (f"rtsp://{args.username}:{args.password}@{args.ip}:554/stream1")
        self.stream_source["video3"] = (f"rtsp://{args.username}:{args.password}@{args.ip}:554/stream2")
        self.start_snapshot_stream()

    def task(self) -> None:
        return

    @classmethod
    def add_parser(cls, parser: argparse.ArgumentParser) -> None:
        super().add_parser(parser)
        parser.add_argument("--username", "-u", required=True, help="Camera username")
        parser.add_argument("--password", "-p", required=True, help="Camera password")

    def start_snapshot_stream(self) -> None:
        print("start_snapshot_stream")
        if not self.snapshot_stream or self.snapshot_stream.poll() is not None:
            cmd = (
                f"ffmpeg -nostdin -y -re -rtsp_transport tcp "
                f'-i {self.stream_source["video3"]} '
                "-r 1 "
                f"-update 1 {self.snapshot_dir}/screen.jpg"
            )
            print(f"Spawning stream for snapshots: {cmd}")
            self.snapshot_stream = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True
            )

    async def get_snapshot(self) -> Path:
        img_file = Path(self.snapshot_dir, "screen.jpg")
        self.start_snapshot_stream()
        return img_file

    async def get_stream_source(self, stream_index: str) -> str:
        print(f"requested stream_index: {stream_index}")
        return self.stream_source[stream_index]

    async def change_video_settings(self, options: dict[str, Any]) -> None:
        print(f"requested change_video_settings: {options}")

    async def process_continuous_move(self, msg: AVClientRequest) -> None:
        xDirection = msg["payload"]["x"]
        yDirection = msg["payload"]["y"]
        print(f"xDirection: {xDirection}")
        #-> cand vine x: -750 => startMotorClockwise()
        #-> cand vine x: 0 => self.cam.moveMotor(5, 0)
        #-> cand vine x: +750 => startMotorCounterClockwise()
        print(f"TAPO process_continuous_move: {msg}")
        if xDirection < 0:
            self.cam.startMotorClockwise()
#             self.xTarget = -self.velocity
        elif xDirection > 0:
            self.cam.startMotorCounterClockwise()
#             self.xTarget = self.velocity
        elif xDirection == 0:
            self.cam.moveMotor(5, 0)
#             self.xTarget = 0

#         if yDirection < 0:
#             self.yTarget = -self.velocity
#         elif yDirection > 0:
#             self.yTarget = self.velocity
#         elif yDirection == 0:
#             self.yTarget = 0
