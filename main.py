import json
import os
import socket
import struct

from handler import ResponseHandler

tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = socket.gethostbyname(socket.gethostname())
print(ip)
# ip_port = (ip, 8021)
ip_port = ("127.0.0.1", 8021)
buffer_size = 1024

# tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
tcp_server.bind(ip_port)
tcp_server.listen(5)

while True:
    '''链接循环'''
    conn, addr = tcp_server.accept()

    print('链接人的信息:', addr)
    while True:
        if not conn:
            print('客户端链接中断')
            break
        '''通信循环'''
        file_msg = "Redbone by Childish Gambino (Looper cover).mp4"

        a = ResponseHandler(conn, "test")
        a.send_dir_info()

        print('发送成功')

        break
    break
