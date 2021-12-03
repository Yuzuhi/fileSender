import socket
import json

from common.logger import logger
from common.exceptions import DisconnectionException
from core.handler import ResponseHandler
from settings import settings

tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = socket.gethostbyname(socket.gethostname())
print(ip)
ip_port = ("0.0.0.0", 8021)
buffer_size = 1024

# tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
tcp_server.bind(ip_port)
tcp_server.listen(5)

handler = ResponseHandler(settings.AnimePath)

while True:
    '''链接循环'''
    conn, addr = tcp_server.accept()
    logger.info(f"来自{addr}的用户链接了服务器")
    while True:
        if not conn:
            logger.info(f"来自{addr}的用户中断了访问")
            break
        '''通信循环'''

        # receive head_info_len
        try:
            request = conn.recv(4)
        except ConnectionResetError:
            logger.error(f"来自{addr}的用户发生错误中断了访问", ConnectionResetError)
            conn.close()
            break
        except TimeoutError:
            logger.error(f"来自{addr}的用户长时间没有应答", TimeoutError)
            conn.close()
            break

        print("接收到request:", str(request, encoding='utf-8'))
        if not request:
            conn.close()
            break

        try:
            handler.distribute(conn, request)
            print(f"success responded the request:{str(request, encoding='utf-8')}")
        except DisconnectionException:
            conn.close()
            logger.error(f"来自{addr}的用户发生错误中断了访问", DisconnectionException)
            break
        except UnicodeDecodeError as e:
            conn.close()
            logger.error(f"来自{addr}的用户请求错误，请求内容为：{str(request, encoding='utf-8')}\n错误为{e}")
            break
        except json.decoder.JSONDecodeError as e:
            conn.close()
            logger.error(f"来自{addr}的用户请求错误，请求内容为：{str(request, encoding='utf-8')}\n错误为{e}")
            break
        except TimeoutError:
            logger.error(f"来自{addr}的用户长时间没有应答", TimeoutError)
            conn.close()
            break
        except Exception as e:
            logger.error(f"来自{addr}的用户连接时发生错误,请求内容为：{request}\n错误为{e}")
            conn.close()
            break
