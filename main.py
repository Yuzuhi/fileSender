import json
import os
import socket
import struct
import time

from exceptions import DisconnectionException
from handler import ResponseHandler

tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = socket.gethostbyname(socket.gethostname())
print(ip)
# ip_port = (ip, 8021)
ip_port = ("172.17.28.71", 8021)
buffer_size = 1024

# tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
tcp_server.bind(ip_port)
tcp_server.listen(5)
tcp_server.settimeout(None)
anime_path = r"C:\Users\Administrator\Desktop\anime"

# listener = ResponseHandler(tcp_server, anime_path)
handler = ResponseHandler(anime_path)

while True:
    '''链接循环'''
    conn, addr = tcp_server.accept()
    print('链接人的信息:', addr)
    while True:
        if not conn:
            print('客户端链接中断')
            break
        '''通信循环'''

        # receive head_info_len
        try:
            request = conn.recv(4)
        except ConnectionResetError:
            conn.close()
            break

        print("接收到request:", request)
        if not request:
            conn.close()
            break

        try:
            handler.distribute(conn, request)
        except DisconnectionException:
            conn.close()
            break
