import socket
import os
import json
import struct
import sys


class ResponseHandler:

    def __init__(self, soc: socket.socket, anime_root_path: str):
        self.socket = soc
        self.anime_root_path = anime_root_path

    def send_dir_info(self):
        dirs = os.listdir(self.anime_root_path)
        dir_dict = {"dirs": dict()}

        for d in dirs:

            if os.path.isdir(os.path.join(self.anime_root_path, d)):
                inner = {
                    d: {
                        "dirName": d,
                        "dirImage": ""
                    }
                }

                dir_dict["dirs"].update(inner)

        data_info = {
            "dirNumbers": len(dirs),
            "dirs": dir_dict
        }

        head_info = {
            "dirNumbers": len(dirs),
            "infoSize": sys.getsizeof(data_info)
        }

        data_info = json.dumps(data_info)

        self._send_head_info(head_info)

        self.socket.send(data_info.encode('utf-8'))

    def send_anime(self, anime_file: str, anime_name: str):

        anime = os.path.join(self.anime_root_path, anime_file)

        head_info = {
            "animeName": anime_name,
            "animeSize": os.path.getsize(anime)
        }

        self._send_head_info(head_info)

        # send anime file
        with open(anime, "rb") as f:
            data = f.read()
            self.socket.sendall(data)

    def _send_head_info(self, head_info: dict):

        head_info = json.dumps(head_info).encode("utf-8")

        head_info_len = struct.pack("i", len(head_info))
        self.socket.send(head_info_len)
        self.socket.send(head_info)
