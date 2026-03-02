import json
from engine.util.redis.redis_util import RedisUtil
from engine.core.context import *

def write_split_record_to_redis(split_record_data_list, context_instance):
    rule_id = context_instance.get('[RULE_ID]')
    file_path_and_name = context_instance.get('[FILE_PATH_AND_NAME]')
    split_record_redis_key = f"fs_record_{rule_id}_{file_path_and_name}"
    json_string = json.dumps(split_record_data_list, ensure_ascii=False)
    # 写入redis
    RedisUtil.set_string(split_record_redis_key, json_string,ex=3600)


if __name__ == '__main__':


    split_record_data_list = []
    split_record_data_dict = {}

    split_record_data_dict['belong_value'] = 'fundId123'
    split_record_data_dict['dest_file_path'] = '/home/publish/test1.txt'
    split_record_data_list.append(split_record_data_dict)

    split_record_data_dict['belong_value'] = 'fund456'
    split_record_data_dict['dest_file_path'] = '/home/publish/test2.txt'
    split_record_data_list.append(split_record_data_dict)

    context_instance = Context()
    context_instance.set('[RULE_ID]', '123456')
    context_instance.set('[FILE_PATH_AND_NAME]', '/home/share/source/test.txt')

    write_split_record_to_redis(split_record_data_list,context_instance)

