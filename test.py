import json
import socket
import struct

tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ip_port = ("127.0.0.1", 8021)
buffer_size = 1024

tcp_server.bind(ip_port)
tcp_server.listen(5)

conn, addr = tcp_server.accept()
request = conn.recv(4)

head_len = struct.unpack('i', request)[0]
print(head_len)
response = conn.recv(head_len)
head_info = json.loads(response.decode('utf-8'))
print("-0" * 100)
print(head_info)
tcp_server.close()