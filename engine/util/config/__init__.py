from engine.util.config.MyConfig import MyConfig


def get_config_value(key_str, default_value=None):
    """
        获取application.yaml配置文件中的值.
        举例:传入 server.port 形式的 key 值，获取对应的值
    """
    try:
        config_value = MyConfig.get_config_value(key_str)
        if config_value is not None:
            return config_value
        else:
            return default_value
    except Exception as e:
        return default_value


def get_root_path():
    return MyConfig.get_root_path()





