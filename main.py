import json
import os
import socket
import struct
import time

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

anime_path = r"C:\Users\Administrator\Desktop\anime"

# listener = ResponseHandler(tcp_server, anime_path)

while True:
    '''链接循环'''
    conn, addr = tcp_server.accept()
    print('链接人的信息:', addr)
    while True:
        if not conn:
            print('客户端链接中断')
            break
        '''通信循环'''
        conn = ResponseHandler(conn, anime_path)
        # receive head_info_len
        request = conn.socket.recv(4)
        # make response
        conn.distribute(request)
        # head_len = struct.unpack('i', request)[0]
        # head_info = json.loads(request.decode('utf-8'))
        time.sleep(0.01)

    time.sleep(0.01)
