import socket
import os
import json
import struct
from typing import Dict, List

from common.logger import logger
from common.exceptions import DisconnectionException
from common.parser import Config
from common.utils import to_bytes
from main import NewPatchPath
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
            self.download_response(conn, request_body)
        elif code == CHECK_UPDATE_COMMAND:
            self.check_update_response(conn, request_body)
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

        print(f"send dir,response:{response_body}")
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
        print(f"send video info,response:{response_body.decode('utf-8')}")
        conn.send(response_body)

    @staticmethod
    def _send_header_info(conn: socket.socket, header_info: bytes):

        header_info_len = struct.pack("i", len(header_info))
        print(f"send header message length,length:{header_info_len}")
        conn.send(header_info_len)
        print(f"send header message,message:{header_info}")
        conn.send(header_info)
        print(f"header_info {header_info} has been sent")

    def download_response(self, conn: socket.socket, request_body: dict):
        """发送客户端所请求的文件"""

        video_path = os.path.join(self.video_root_path, request_body["videoDir"], request_body["videoName"])
        video_size = os.path.getsize(video_path)

        header_info = to_bytes(
            command="download",
            code=SUCCESS_CODE,
            videoSize=video_size
        )

        self._send_header_info(conn, header_info)

        received = request_body.get("received", 0)
        # 设置session超时时间
        conn.settimeout(10)
        print(f"send videos:{video_path}")
        try:
            with open(video_path, "rb") as f:
                f.seek(received)
                conn.sendall(f.read())
            logger.info(f"videos {video_path} which been sent to {conn.getpeername()} has been completed")
            conn.settimeout(None)
        except Exception as e:
            raise e

    def check_update_response(self, conn: socket.socket, request_body: dict):
        files = os.listdir(NewPatchPath)

        version = ""

        if len(files) >= 2:
            for file in files:
                if file == CONFIG_FILE:
                    version = Config.get("project").get("version")

        response_body = to_bytes(
            command="version",
            version=version
        )

        header_info = to_bytes(
            command="version",
            code=SUCCESS_CODE,
            msgSize=len(response_body)
        )

        self._send_header_info(conn, header_info)
        print(f"send update information,response:{response_body.decode('utf-8')}")
        conn.send(response_body)
