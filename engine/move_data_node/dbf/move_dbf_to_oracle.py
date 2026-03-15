import pandas as pd
from simpledbfdm import Dbf5


from engine.core.migrate_core_engine import *
import engine.util.config as config
from dbfreaddm import DBF as DBFREAD_DBF

from engine.util.redis.redis_util import RedisUtil
from engine.util.http.http_client import HttpClient


def move_dbf_to_oracle(flow_node, file_path_and_name, flow_node_dbf_config, field_mapping_config_list, context_instance):

    try:
        # 执行并发读取控制
        #concurrent_read_control(file_path_and_name)

        # 默认使用simpledbfdm读取dbf文件的开关值
        default_switch_count = 100000
        using_multi_process_switch_count = config.get_config_value('dbf.using_multi_process_switch_count',  default_switch_count)

        # 创建读数引擎
        migrate_core_engine = MigrateCoreEngine()
        filter_logic = flow_node_dbf_config.get('filterLogic')
        target_interface_table = flow_node_dbf_config['targetIntfTbl']
        my_uuid = context_instance.get('[UUID]')
        interface_id = context_instance.get('[INTERFACE_ID]')

        try:
            log.info("uuid: %s,开始使用simpledbfdm读取dbf文件", my_uuid)
            start_time = time.time()

            my_dbf = Dbf5(file_path_and_name, codec='gbk')
            end_time = time.time()
            log.info("uuid: %s,加载dbf文件耗时:%s秒, 记录数：%s", my_uuid, end_time - start_time, my_dbf.numrec)

            # 大文件请求场景 & 接口ID为000001预热接口场景 --------发起大文件读取-----start----------

            # 这里判断，如果是大文件，则发起http请求，请求/execute/read_big_file，然后等待返回结果，
            if my_dbf.numrec > using_multi_process_switch_count or interface_id == '000001':
                # 通过http请求，请求/execute/read_big_file
                read_command = context_instance.get('[READ_COMMAND]')
                invoke_read_big_file(read_command, my_uuid)
                # 不能把return去掉，重要！重要！重要！的事情说3遍！
                return
            # 大文件请求场景 & 接口ID为000001预热接口场景 --------发起大文件读取-----end----------
            else:
                # 正常读取dbf文件-----------------------start--------------------------------
                my_df = my_dbf.to_dataframe()
                end_time = time.time()
                log.info("uuid: %s,读取dbf块文件耗时:%s秒, 记录数：%s", my_uuid, end_time - start_time, len(my_df))
                # 调用核心引擎，将dataframe数据插入数据库
                migrate_core_engine.dataframe_to_oracle(flow_node_dbf_config,
                                                        my_df, filter_logic,
                                                        target_interface_table,
                                                        field_mapping_config_list,
                                                        context_instance)
                # 正常读取dbf文件-----------------------end--------------------------------

        except AssertionError as e:  # 如果出现这个错误，说明使用simpledbf读取dbf文件出现问题,尝试使用dbfread库读取dbf文件
            log.info("uuid: %s,开始使用DBFREAD_DBF读取dbf文件", my_uuid)
            start_time = time.time()
            table = DBFREAD_DBF(file_path_and_name, encoding='gbk')


            # 大文件请求场景 & 接口ID为000001预热接口场景 --------发起大文件读取-----start----------
            # 这里判断，如果是大文件，则发起http请求，请求/execute/read_big_file，然后等待返回结果
            if len(table) > using_multi_process_switch_count or interface_id == '000001':
                # 通过http请求，请求/execute/read_big_file
                read_command = context_instance.get('[READ_COMMAND]')
                log.info("uuid: %s,发起http请求，请求/execute/read_big_file", my_uuid)
                invoke_read_big_file(read_command, my_uuid)
                log.info("uuid: %s,发起http请求，请求/execute/read_big_file, 完成", my_uuid)
                # 不能把return去掉，重要！重要！重要！的事情说3遍！
                return
            # 大文件请求场景 & 接口ID为000001预热接口场景 --------发起大文件读取-----end----------
            else:
                # 正常读取dbf文件-----------------------start-------------------------------
                my_dbf = pd.DataFrame(iter(table))
                end_time = time.time()
                log.info("uuid: %s,读取dbf块文件耗时:%s秒, 记录数：%s", my_uuid, end_time - start_time, len(my_dbf))
                # 调用核心引擎，将dataframe数据插入数据库
                migrate_core_engine.dataframe_to_oracle(flow_node_dbf_config,
                                                        my_dbf, filter_logic,
                                                        target_interface_table,
                                                        field_mapping_config_list,
                                                        context_instance)
                # 正常读取dbf文件-----------------------end--------------------------------


    finally:
        pass
        # 释放并发读取锁
        #release_read_lock(file_path_and_name)



def invoke_read_big_file(read_command, uuid=None):
    """
    调用/execute/read_big_file接口，读取大文件
    :param uuid: 请求的唯一标识符，可选。
    :param read_command: 读取命令
    :return:
    """
    # 创建 HttpClient 实例
    client = HttpClient()

    # 发送 POST 请求
    post_url = "http://localhost:28888/execute/read_big_file"
    post_body = read_command
    response = client.post(post_url, post_body, uuid=uuid)

    # 检查请求是否成功
    if response.status_code == 200:
        # response.json()为:
        # {'msg':'操作成功',
        #  'code': 200,
        # }
        json_data = response.json()
        if json_data['code'] == 200:
            return True
        else:
            raise Exception('请求失败，错误信息：' + json_data['msg'])
    else:
        raise Exception(f'请求失败，状态码：{response.status_code}, 错误信息：{response.text}')


def concurrent_read_control(file_path_and_name):
    """
        控制逻辑：同一时刻，控制只能有一个地方读取同一个 DBF 文件，
        同时读取将导致耗时急剧增加（问题：碰到一个空文件，并发读取耗时35秒）
        :param file_path_and_name: DBF 文件的路径和名称
    """
    file_key = f"dbf_read:{file_path_and_name}"
    count = 0
    while True:
        # 尝试将文件名称写入 Redis，若写入成功则表示可以开始读取. 自动超时时间为60秒
        if RedisUtil.set_string_not_exists(file_key, 1, ex=60, nx=True):
            break
        # 若 Redis 里已有对应值，等待 100ms 后再次尝试
        time.sleep(0.1)
        count = count + 1
        if count > 600:
            break


def release_read_lock(file_path_and_name):
    """
    释放并发读取锁
    :param file_path_and_name: DBF 文件的路径和名称
    """
    file_key = f"dbf_read:{file_path_and_name}"
    RedisUtil.delete_key(file_key)

def dbf_to_dataframe(file_path_and_name):
    start_time = time.time()
    dbf = Dbf5(file_path_and_name, codec='gbk')

    df = dbf.to_dataframe()
    end_time = time.time()

    # 获取字段名称
    field_names = df.columns
    # print("字段名称:", field_names)
    # 将Index对象转换成列表
    index_list = field_names.tolist()
    print("字段名称:", index_list)



    print('python 加载dbf文件耗时:', end_time - start_time, '秒, 记录数：', dbf.numrec)
    return df


