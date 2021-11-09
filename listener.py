import json
import socket


def listen(tcp_server: socket.socket, buffer_size: int = 1024):
    while True:
        conn, addr = tcp_server.accept()
        print('链接人的信息:', addr)

        while True:
            if not conn:
                print('客户端连接中断')
                break

            msg = tcp_server.recv(buffer_size)
            msg = json.loads(msg.decode("utf-8"))
