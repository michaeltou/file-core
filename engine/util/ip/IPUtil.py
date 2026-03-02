import socket


class IPUtil(object):

    ip_address = None

    @classmethod
    def get_ip(cls):
        if cls.ip_address is None:
            cls.ip_address = cls.get_local_ip_address()
        return cls.ip_address

    @classmethod
    def get_local_ip_address(cls):
        # 获取主机名
        hostname = socket.gethostname()
        # 获取IP地址列表
        ip_addresses = socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_IP,
                                          socket.AI_PASSIVE)
        # 从列表中选择第一个非回环地址作为局域网IP地址
        local_ip_address = None
        for addr in ip_addresses:
            if addr[0] == socket.AF_INET and not addr[4][0].startswith('127.'):
                local_ip_address = addr[4][0]
                break
        return local_ip_address

