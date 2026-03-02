import yaml
import os


class MyConfig(object):
    config = None

    root_path = None

    @classmethod
    def get_root_path(cls):
        cls._init_config_if_not_initialized()
        return cls.root_path

    @classmethod
    def find_application_yaml(cls):
        current_directory = os.getcwd()
        while current_directory != os.path.dirname(current_directory):  # 避免无限循环
            file_path = os.path.join(current_directory, "application.yaml")
            if os.path.exists(file_path):
                cls.root_path = current_directory
                return file_path
            current_directory = os.path.dirname(current_directory)
        return None  # 如果没有找到文件

    @classmethod
    def _init_config_if_not_initialized(cls):
        if not cls.config:
            file_path = cls.find_application_yaml()
            # print("config file path: ", file_path)
            if file_path:
                with open(file_path, "r") as f:
                    cls.config = yaml.safe_load(f)

    @classmethod
    def get_config_value(cls, key_str):
        cls._init_config_if_not_initialized()
        keys = key_str.split(".")
        value = cls.config
        for key in keys:
            value = value.get(key)
        return value


if __name__ == "__main__":
    # print(MyConfig.get_config_value("mysql.host"))
    # print(MyConfig.get_config_value("mysql.port"))
    print(MyConfig.get_config_value("redis.database"))


