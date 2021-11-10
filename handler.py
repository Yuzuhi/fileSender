import socket
import os
import json
import struct
import sys
from typing import Dict, List

from constant import *
from utils import to_bytes


class ResponseHandler:

    def __init__(self, soc: socket.socket, video_root_path: str):
        self.socket = soc
        self.video_root_path = video_root_path

    def distribute(self, head_len: bytes):
        """
        根据客户端发来的头部信息来分发至处理该信息的相关函数
        :param head_len:
        :return:
        """

        head_len = struct.unpack('i', head_len)[0]
        head_info = self.socket.recv(head_len)
        print("收到消息：", head_info)
        if not head_len:
            raise socket.error

        head_info = json.loads(head_info.decode('utf-8'))
        code = head_info["code"]

        request_body_len = head_info["msgSize"]
        request_body = self.socket.recv(request_body_len)
        if not request_body:
            raise socket.error

        request_body = json.loads(request_body.decode('utf-8'))

        if code == GET_DIRS_COMMAND:
            self.dirs_info_response(request_body)

        elif code == GET_FILES_COMMAND:
            self.video_info_response(request_body)

        elif code == DOWNLOAD_COMMAND:
            self.send_video_response(request_body)
        else:
            return

    def _dirs_info(self) -> [Dict, Dict]:

        dirs = os.listdir(self.video_root_path)

        response_body = {
            "command": "getDirs",
            "code": SUCCESS_CODE,
            "dirNumbers": len(dirs),
            "dirs": dict()
        }

        for d in dirs:

            if os.path.isdir(os.path.join(self.video_root_path, d)):
                inner = {
                    d: {
                        "dirName": d,
                        "dirImage": ""
                    }
                }

                response_body["dirs"].update(inner)

        head_info = {
            "dirNumbers": len(dirs),
            "msgSize": sys.getsizeof(response_body)
        }

        return head_info, response_body

    def dirs_info_response(self, request_body: dict):
        """
        发送服务器资源根目录下的所有视频文件夹信息
        :param request_body:
        :return:
        """

        head_info, response_body = self._dirs_info()

        head_info = json.dumps(head_info).encode("utf-8")

        if not head_info:
            return

        self._send_head_info(head_info)
        response_body = json.dumps(response_body).encode('utf-8')
        print("发送response_body:", response_body)
        self.socket.send(response_body)

    def _get_video_info(self, video_file_list: List[str]) -> dict:
        """发送每个文件夹内的剧集信息"""

        response_body = {
            "command": "getVideos",
            "code": SUCCESS_CODE,
            "dirNumber": len(video_file_list)
        }

        dirs = dict()

        for video_dir in video_file_list:
            dirs.setdefault(video_dir, dict())

            video_file = os.path.join(self.video_root_path, video_dir)

            for _, _, files in os.walk(video_file):
                dirs[video_dir]["fileNumber"] = len(files)
                for file in files:
                    dirs[video_dir][file] = {
                        "fileName": file,
                        "fileImage": ""
                    }

        response_body["dirs"] = dirs

        return response_body

    def video_info_response(self, request_body: dict):
        """
        根据请求的视频文件夹名发送服务器上的该视频文件夹下的文件信息
        :param request_body:
        :return:
        """

        file_path_list = request_body["dirName"]

        video_dict = self._get_video_info(file_path_list)

        response_body = to_bytes(**video_dict)

        head_info = to_bytes(
            command="getFiles",
            code=GET_FILES_COMMAND,
            msgSize=sys.getsizeof(response_body)
        )

        self._send_head_info(head_info)
        self.socket.send(response_body)

    def _send_head_info(self, head_info: bytes):

        head_info_len = struct.pack("i", len(head_info))
        self.socket.send(head_info_len)

        try:
            self.socket.send(head_info)
        except Exception:
            self._send_error_code()

    def send_video_response(self, request_body: dict):
        """发送客户端所请求的文件"""

        video_path = os.path.join(self.video_root_path, request_body["videoDir"], request_body["videoName"])

        head_info = to_bytes(
            command="download",
            code=SUCCESS_CODE,
            msgSize=sys.getsizeof(video_path)
        )

        self._send_head_info(head_info)

        try:
            with open(video_path, "rb") as f:
                self.socket.sendall(f.read())
        except Exception:
            self._send_error_code()

    def _send_error_code(self):
        error_info = to_bytes(
            commend=FAIL_CODE
        )
        self.socket.send(error_info)
