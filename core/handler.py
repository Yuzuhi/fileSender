import socket
import os
import json
import struct
from typing import Dict, List

from common.logger import logger
from common.exceptions import DisconnectionException
from common.utils import to_bytes
from .constant import *


class ResponseHandler:

    def __init__(self, video_root_path: str):
        self.video_root_path = video_root_path

    def distribute(self, conn: socket.socket, head_len: bytes):
        """
        根据客户端发来的头部信息来分发至处理该信息的相关函数
        :param conn:
        :param head_len:
        :return:
        """

        head_len = struct.unpack('i', head_len)[0]
        header_info = conn.recv(head_len)
        if not header_info:
            raise DisconnectionException

        header_info = json.loads(header_info.decode('utf-8'))
        code = header_info["code"]

        request_body_len = header_info["msgSize"]
        request_body = conn.recv(request_body_len)
        if not request_body:
            raise DisconnectionException

        request_body = json.loads(request_body.decode('utf-8'))

        if code == GET_DIRS_COMMAND:
            self.dirs_info_response(conn, request_body)

        elif code == GET_FILES_COMMAND:
            self.video_info_response(conn, request_body)

        elif code == DOWNLOAD_COMMAND:
            self.send_video_response(conn, request_body)
        else:
            return

    def _dirs_info(self) -> [Dict, bytes]:

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

        response_body = json.dumps(response_body).encode('utf-8')

        header_info = {
            "dirNumbers": len(dirs),
            "msgSize": len(response_body)
        }

        return header_info, response_body

    def dirs_info_response(self, conn: socket.socket, request_body: dict):
        """
        发送服务器资源根目录下的所有视频文件夹信息
        :param conn:
        :param request_body:
        :return:
        """

        header_info, response_body = self._dirs_info()

        header_info = json.dumps(header_info).encode("utf-8")

        if not header_info:
            return

        self._send_header_info(conn, header_info)

        print(f"发送response_body:{response_body}，长度为{len(response_body)}")
        conn.send(response_body)

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
                dirs[video_dir]["videoNumber"] = len(files)
                for file in files:
                    dirs[video_dir][file] = {
                        "videoName": file,
                        "videoImage": ""
                    }

        response_body["dirs"] = dirs

        return response_body

    def video_info_response(self, conn: socket.socket, request_body: dict):
        """
        根据请求的视频文件夹名发送服务器上的该视频文件夹下的文件信息
        :param conn:
        :param request_body:
        :return:
        """

        file_path_list = request_body["dirName"]

        video_dict = self._get_video_info(file_path_list)

        response_body = to_bytes(**video_dict)

        header_info = to_bytes(
            command="getVideos",
            code=GET_FILES_COMMAND,
            msgSize=len(response_body)
        )

        self._send_header_info(conn, header_info)
        conn.send(response_body)

    def _send_header_info(self, conn: socket.socket, head_info: bytes):

        header_info_len = struct.pack("i", len(head_info))
        conn.send(header_info_len)

        try:
            print(f"发送header:{head_info}长度为{len(head_info)}")
            conn.send(head_info)
        except Exception:
            self._send_error_code(conn)

    def send_video_response(self, conn: socket.socket, request_body: dict):
        """发送客户端所请求的文件"""

        video_path = os.path.join(self.video_root_path, request_body["videoDir"], request_body["videoName"])
        print("要下载的文件为：", video_path)
        video_size = os.path.getsize(video_path)

        header_info = to_bytes(
            command="download",
            code=SUCCESS_CODE,
            videoSize=video_size
        )

        self._send_header_info(conn, header_info)

        received = request_body.get("received", 0)

        try:
            with open(video_path, "rb") as f:
                f.seek(received)
                conn.sendall(f.read())
            logger.info(f"向{conn.getsockname()}发送的{video_path}已发送完成")
        except Exception:
            self._send_error_code(conn)

    @staticmethod
    def _send_error_code(conn: socket.socket):
        error_info = to_bytes(
            commend=FAIL_CODE
        )
        conn.send(error_info)
