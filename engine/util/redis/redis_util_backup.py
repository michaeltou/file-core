import redis
import engine.util.config as config
from redis.cluster import RedisCluster

class RedisUtil:
    _redis_pool = None
    _redis_instance = None

    @staticmethod
    def _is_cluster_mode():
        """
        检查是否为集群模式
        """
        return config.get_config_value("redis.cluster") == True

    @staticmethod
    def _get_redis_pool():
        if RedisUtil._redis_pool is None:
            if RedisUtil._is_cluster_mode():
                # 集群模式
                redis_nodes = config.get_config_value("redis.nodes")
                if not redis_nodes:
                    raise ValueError("redis集群节点配置缺失.")

                # 解析节点列表，格式为 "host1:port1,host2:port2"
                nodes = []
                for node in redis_nodes.split(","):
                    host, port = node.strip().split(":")

                    # 创建一个具有 name 属性的节点对象
                    class Node:
                        def __init__(self, host, port):
                            self.host = host
                            self.port = port
                            self.name = f"{host}:{port}"

                    nodes.append(Node(host, port))

                # 对于集群模式，存储节点列表
                RedisUtil._redis_pool = nodes
            else:
                # 单实例模式
                redis_host = config.get_config_value("redis.host")
                redis_port = config.get_config_value("redis.port")
                redis_database = config.get_config_value("redis.database")
                redis_password = config.get_config_value("redis.password")

                if not redis_host or not redis_port:
                    raise ValueError("redis相关参数.")

                RedisUtil._redis_pool = redis.ConnectionPool(
                    host=redis_host,
                    port=int(redis_port),
                    db=int(redis_database),
                    password=redis_password,
                    max_connections=300,  # 最大连接数
                    socket_timeout=300,  # 读写超时时间为 300 秒
                    socket_connect_timeout=30  # 连接超时时间为 30 秒
                )
        return RedisUtil._redis_pool

    @staticmethod
    def _get_redis_instance():
        if RedisUtil._redis_instance is None:
            pool = RedisUtil._get_redis_pool()
            redis_password = config.get_config_value("redis.password")

            if RedisUtil._is_cluster_mode():
                # 集群模式
                RedisUtil._redis_instance = RedisCluster(
                    startup_nodes=pool,  # pool在这里是nodes列表
                    password=redis_password,
                    decode_responses=True,  # 自动解码响应
                    max_connections=300,  # 最大连接数
                    socket_timeout=300,  # 读写超时时间为 300 秒
                    socket_connect_timeout=30  # 连接超时时间为 30 秒
                )
            else:
                # 单实例模式
                RedisUtil._redis_instance = redis.Redis(
                    connection_pool=pool,
                    decode_responses=True  # 自动解码响应
                )
        return RedisUtil._redis_instance


    @staticmethod
    def set_string(key, value, ex=None):
        """
        设置字符串类型的键值对

        :param key: 键
        :param value: 值
        :param ex: 过期时间（秒）
        :return: 设置成功返回 True，失败返回 False
        """
        r = RedisUtil._get_redis_instance()
        return r.set(key, value, ex=ex)

    @staticmethod
    def set_string_not_exists(key, value, ex=None,nx=False):
        """
        设置字符串类型的键值对

        :param key: 键
        :param value: 值
        :param ex: 过期时间（秒）
        :param nx: 如果设置为 True，则只有 name 不存在时，当前 SET 操作才执行
        :return: 设置成功返回 True，失败返回 False
        """
        r = RedisUtil._get_redis_instance()
        return r.set(key, value, ex=ex,nx=nx)

    @staticmethod
    def get_string(key):
        """
        获取字符串类型的键对应的值

        :param key: 键
        :return: 键对应的值，如果键不存在返回 None
        """
        r = RedisUtil._get_redis_instance()
        result = r.get(key)
        return result.decode('utf-8') if result else None

    @staticmethod
    def delete_key(key):
        """
        删除指定的键

        :param key: 要删除的键
        :return: 删除成功返回删除的键的数量，失败返回 0
        """
        r = RedisUtil._get_redis_instance()
        return r.delete(key)

    @staticmethod
    def hset(name, key, value):
        """
        设置哈希类型的字段值

        :param name: 哈希的名称
        :param key: 字段名
        :param value: 字段值
        :return: 设置成功返回 1，字段已存在返回 0
        """
        r = RedisUtil._get_redis_instance()
        return r.hset(name, key, value)

    @staticmethod
    def hget(name, key):
        """
        获取哈希类型的指定字段的值

        :param name: 哈希的名称
        :param key: 字段名
        :return: 字段的值，如果字段不存在返回 None
        """
        r = RedisUtil._get_redis_instance()
        result = r.hget(name, key)
        return result.decode('utf-8') if result else None

    @staticmethod
    def hgetall(name):
        """
        获取哈希类型的所有字段和值

        :param name: 哈希的名称
        :return: 包含所有字段和值的字典
        """
        r = RedisUtil._get_redis_instance()
        result = r.hgetall(name)
        return {k.decode('utf-8'): v.decode('utf-8') for k, v in result.items()}

    @staticmethod
    def lpush(key, *values):
        """
        向列表左侧插入元素

        :param key: 列表的键
        :param values: 要插入的元素
        :return: 插入元素后列表的长度
        """
        r = RedisUtil._get_redis_instance()
        return r.lpush(key, *values)

    @staticmethod
    def rpop(key):
        """
        从列表右侧弹出元素

        :param key: 列表的键
        :return: 弹出的元素，如果列表为空返回 None
        """
        r = RedisUtil._get_redis_instance()
        result = r.rpop(key)
        return result.decode('utf-8') if result else None

    @staticmethod
    def llen(key):
        """
        获取列表的长度

        :param key: 列表的键
        :return: 列表的长度
        """
        r = RedisUtil._get_redis_instance()
        return r.llen(key)

    @staticmethod
    def sadd(key, *values):
        """
        向集合中添加元素

        :param key: 集合的键
        :param values: 要添加的元素
        :return: 添加成功的元素数量
        """
        r = RedisUtil._get_redis_instance()
        return r.sadd(key, *values)

    @staticmethod
    def sismember(key, value):
        """
        检查元素是否在集合中

        :param key: 集合的键
        :param value: 要检查的元素
        :return: 如果元素在集合中返回 True，否则返回 False
        """
        r = RedisUtil._get_redis_instance()
        return r.sismember(key, value)

    @staticmethod
    def smembers(key):
        """
        获取集合中的所有元素

        :param key: 集合的键
        :return: 包含集合所有元素的列表
        """
        r = RedisUtil._get_redis_instance()
        result = r.smembers(key)
        return [v.decode('utf-8') for v in result]

    @staticmethod
    def zadd(name, mapping):
        """
        向有序集合中添加元素

        :param name: 有序集合的名称
        :param mapping: 包含元素和分数的字典
        :return: 添加成功的元素数量
        """
        r = RedisUtil._get_redis_instance()
        return r.zadd(name, mapping)

    @staticmethod
    def zscore(name, member):
        """
        获取有序集合中元素的分数

        :param name: 有序集合的名称
        :param member: 元素
        :return: 元素的分数，如果元素不存在返回 None
        """
        r = RedisUtil._get_redis_instance()
        return r.zscore(name, member)

    @staticmethod
    def zrevrange(name, start, end, withscores=False):
        """
        获取有序集合中排名前 n 的元素

        :param name: 有序集合的名称
        :param start: 起始索引
        :param end: 结束索引
        :param withscores: 是否返回分数
        :return: 包含元素（和分数）的列表
        """
        r = RedisUtil._get_redis_instance()
        result = r.zrevrange(name, start, end, withscores=withscores)
        if withscores:
            return [(k.decode('utf-8'), v) for k, v in result]
        return [k.decode('utf-8') for k in result]

    @staticmethod
    def close():
        """
        关闭 Redis 连接
        """
        if RedisUtil._redis_instance:
            RedisUtil._redis_instance.close()
            RedisUtil._redis_instance = None
