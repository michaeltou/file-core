from datetime import datetime
from decimal import Decimal

import socket


def get_ip_address():
    # 获取主机名
    hostname = socket.gethostname()
    # 获取IP地址
    ip_address = socket.gethostbyname(hostname)
    return ip_address


# 获取本机IP地址
ip_address = get_ip_address()
print("本机IP地址:", ip_address)