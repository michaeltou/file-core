import json

if __name__ == '__main__':
    belong_value_and_publish_path_dict = {
        "归属值1": "/路径/发布/1",
        "归属值2": "/路径/发布/2"
    }

    # 显示原始的非 ASCII 字符
    json_string = json.dumps(belong_value_and_publish_path_dict, ensure_ascii=False )
    print(json_string)