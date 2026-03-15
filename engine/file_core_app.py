import uuid
import json
from flask import Flask, request, render_template
from waitress import serve
from engine.cnst.NodeType import *

from engine.move_data_node.move_data_engine import move_data

# from engine.execute_sql_node.execute_sql_engine import execute_node_sql
# from engine.build_context_node.build_context_engine import build_context
from engine.core.context import *
# from engine.check_node.check_node_engine import check_node
# from engine.cnst.StatusType import *
# from engine.cnst.PhaseType import *

import engine.util.config as config
import traceback
# import engine.util.performace as performace
# import engine.split.record as record
import engine.util.log as log
import engine.util.time as time
import os
import threading
import time
from ratelimit import limits, sleep_and_retry, RateLimitException
from engine.util.md5 import get_file_md5
from engine.util.redis.redis_util import RedisUtil
from sqlalchemy import create_engine
# from engine.db.oracle_read_tool_db_util import execute_ddl_sql

# WAITRESS  Werkzeug  使用 Gunicorn 启动多个实例
app = Flask(__name__)



# 预热函数
def pre_warm():

    pre_warm_switch = config.get_config_value("read_tool.pre_warm.switch",False)
    if not pre_warm_switch:
        log.info("预热功能未开启，跳过预热操作")
        return
    log.info("预热功能未开启，正在执行预热操作...")
    read_command_json_str = (' {"businessDate": 20241212, "filePathAndName": "PRE_WARM_DBF.FILE", '
                             '"fundCode": "code_666", "fundId": "666", "interfaceId": "000001", '
                             '"interfaceName": "预热接口", '
                             '"needRateLimitControl": 1, "readMode": 3, '
                             '"readRule": {"createTime": 20250729.132848, '
                             '"flowNodeList": [{"fieldMappingConfigList": [{"createTime": 20250729.132849, "fieldType": 1, "interfaceId": "000001", '
                             '"nodeId": "59432145-33e1-4553-a6a3-ade0acb83ecc", '
                             '"processLogicType": 1, "sequence": 3, "sourceField": "SCDM", '
                             '"targetField": "SCDM", "updateTime": 20250729.132849}], '
                             '"flowNodeBasic": {"createTime": 20250729.132849, "fileType": 1, "interfaceId": "000001", "nodeId": "59432145-33e1-4553-a6a3-ade0acb83ecc", "nodeName": "\u7cfb\u7edf\u9884\u70ed\u8282\u70b9", '
                             '"nodeSeqNo": 1, "nodeType": 1, "updateTime": 20250729.132849}, "flowNodeDbfConfig": {"checkLogicSwitch": 1, "createTime": 20250729.132848, "fileType": 1, "interfaceId": "000001", "nodeId": "59432145-33e1-4553-a6a3-ade0acb83ecc", "nodeName": "\u7cfb\u7edf\u9884\u70ed\u8282\u70b9",'
                             ' "nodeSeqNo": 1, "nodeType": 1, "targetIntfTbl": "TM_PRE_WARM", "updateTime": 20250729.132848}, '
                             '"flowNodeRenameConfigList": [{"createTime": 20250729.132849, "interfaceId": "000001", '
                             '"nodeId": "59432145-33e1-4553-a6a3-ade0acb83ecc", "sequence": 1, "updateTime": 20250729.132849}]}],'
                             ' "interfaceId": "000001", "interfaceName": "预热接口",'
                             ' "updateTime": 20250729.132848}}')
    # 这里添加你的预热逻辑，例如数据库连接、表结构检查等
    execute_read(read_command_json_str)



@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/test', methods=['GET', 'POST'])
def test():
    api_limit_call()
    # 获取当前进程号
    process_id = os.getpid()
    # 获取当前线程号
    thread_id = threading.current_thread().ident
    # 生成UUID
    my_uuid = generate_uuid()
    log.info('[进程ID：%s,线程ID：%s]开始执行：uuid：%s',process_id, thread_id, my_uuid)
    time.sleep(1)  # 模拟耗时操作
    log.info('[进程ID：%s,线程ID：%s]结束执行：uuid：%s', process_id, thread_id,my_uuid)
    return build_success_result(f'health check is ok. Process ID: {process_id}, Thread ID: {thread_id}')


@app.route('/health', methods=['GET', 'POST'])
def health():
    # 获取当前进程号
    process_id = os.getpid()
    # 获取当前线程号
    thread_id = threading.current_thread().ident
    return build_success_result(f'health check is ok. Process ID: {process_id}, Thread ID: {thread_id}')


@app.route('/limit', methods=['GET', 'POST'])
def limit():
    try:
        api_limit_call()
        time.sleep(1)  # 模拟耗时操作
        # 获取当前进程号
        process_id = os.getpid()
        # 获取当前线程号
        thread_id = threading.current_thread().ident
        return build_success_result(f'health check is ok. Process ID: {process_id}, Thread ID: {thread_id}')
    except RateLimitException as e:
        return build_limit_error_result(f'access limit is exceeded.')


@app.errorhandler(Exception)
def handle_exception(e):
    tb = traceback.format_exc()
    log.error(f"tmtools 1: 发生未知异常，异常信息: {str(e)}\n{tb}")
    return build_error_result("tmtools 2: 发生未知异常，异常信息. Please check the server logs. "+ str(e)   + tb)



@app.route('/execute/script', methods=['POST'])
def execute_script(script_command_json_str = None):
    if script_command_json_str is None:
        script_command = request.get_json()
    else:
        # 把 JSON 字符串转换回 Python 对象
        script_command = json.loads(script_command_json_str)

    script = script_command.get('script')
    if script is None:
        return build_error_result("脚本内容不能为空")
    exec(script)
    return build_success_result("script executed successfully.")

# 从文件中读取所有的脚本，然后一次性执行
@app.route('/execute/filesScript', methods=['POST'])
def execute_file_script(script_command_json_str = None):
    if script_command_json_str is None:
        script_command = request.get_json()

    file_path_and_name = script_command.get('file_path_and_name')
    if file_path_and_name is None:
        return build_error_result("文件路径不能为空")

    script = '';
    # 读取文件所有的内容，然后一次性执行
    with open(file_path_and_name, 'r') as file:
        script = script + file.read()
    exec(script)
    return build_success_result("script executed successfully.")



@app.route('/execute/read', methods=['POST'])
def execute_read(read_command_json_str = None):
    my_uuid = generate_uuid()
    if read_command_json_str is None:
        read_command = request.get_json()
    else:
        # 把 JSON 字符串转换回 Python 对象
        read_command = json.loads(read_command_json_str)

    # read_command_json_str  = json.dumps(read_command)
    # log.info('UUID: %s,接收到读数请求,读数指令read_command是: %s', my_uuid, read_command_json_str)
    # 获取当前进程号
    process_id = os.getpid()
    # 获取当前线程号
    thread_id = threading.current_thread().ident
    parent_uuid = read_command.get('parentUuid')

    log.info('UUID: %s, 父UUID: %s,接收到读数请求,读数指令read_command是: %s,进程ID：%s,线程ID：%s',
             my_uuid,parent_uuid, read_command, process_id, thread_id)
    file_path_and_name = read_command.get('filePathAndName')

    read_rule = read_command.get('readRule')
    encoding = read_command.get('encoding','utf-8')
    file_id = read_command.get('fileId')
    file_name = read_command.get('fileName')

    need_rate_limit_control = read_command.get('needRateLimitControl')
    fund_id = read_command.get('fundId')
    fund_code = read_command.get('fundCode')
    business_date = read_command.get('businessDate')
    context_map = read_command.get('contextMap')
    flow_node_list = read_rule.get('flowNodeList')
    invoke_mode = read_command.get('invokeMode')


    context_instance = Context()
    context_instance.set('[FUND_ID]', fund_id)
    context_instance.set('[FUND_CODE]', fund_code)
    context_instance.set('[BUSINESS_DATE]', business_date)
    context_instance.set('[INTERFACE_ID]', file_id)
    context_instance.set('[INTERFACE_NAME]', file_name)
    context_instance.set('[FILE_PATH_AND_NAME]', file_path_and_name)
    context_instance.set('[INVOKE_MODE]', invoke_mode)
    context_instance.set('[UUID]', my_uuid)
    context_instance.set('[READ_COMMAND]',read_command)
    context_instance.set('[ENCODING]', encoding)
    # 把传入的context_map 放到上下文里面
    if context_map is not None:
        for key, value in context_map.items():
            context_instance.set('['+ key + ']', value)



    start_time = get_local_millisecond_timestamp()

    # ---------start

    # ---------end
    try:
        # 根据外部传入的限流配置，决定是否进行限流,need_rate_limit_control为1时，表示需要限流,为2时表示不需要限流
        if need_rate_limit_control is not None and need_rate_limit_control == 1:
            api_limit_call()
        if need_rate_limit_control is None:
            api_limit_call()

        for flow_node in flow_node_list:
            file_type = flow_node.get('fileFmt')
            move_data(file_type, file_path_and_name, flow_node, context_instance)

        data_list = context_instance.get('[__DATA_LIST__]')
        field_name_list = context_instance.get('[__FIELD_NAME_LIST__]')
        read_data = {"dataList": data_list, "fieldNameList": field_name_list}

        end_time = get_local_millisecond_timestamp()
        # performace.insert_performance_log(context_instance=context_instance,
        #                                   phase=PhaseType.ALL.value,
        #                                   status=StatusType.SUCCESS.value,
        #                                   message="success",
        #                                   start_time=start_time,
        #                                   end_time=end_time)
        log.info('UUID: %s,父UUID: %s,读数请求处理成功,总体耗时：%s ms', my_uuid, parent_uuid, end_time-start_time)
        return build_success_result(read_data)
    except RateLimitException as e:
        message = 'uuid:%s,发生限流,读数请求处理失败,异常信息：%s' % (my_uuid, 'access limit is exceeded.')
        log.error(message)
        end_time = get_local_millisecond_timestamp()
        # performace.insert_performance_log(context_instance=context_instance,
        #                                   phase=PhaseType.ALL.value,
        #                                   status=StatusType.FAILED.value,
        #                                   message=message,
        #                                   start_time=start_time,
        #                                   end_time=end_time)
        return build_limit_error_result(f'access limit is exceeded.')
    except Exception as e:
        check_logic_result = context_instance.get('check_logic_result')
        if check_logic_result is False:
            check_logic_message = context_instance.get('check_logic_message')
            message = 'uuid:%s,检查逻辑检查不通过,详细信息是:%s' % (my_uuid, check_logic_message)
        else:
            stack_trace = traceback.format_exc()
            if 'resource busy' in stack_trace:
                stack_trace = '文件正在被其他进程占用，请稍后再试。'
            message = 'uuid:%s,读数请求处理失败,异常信息：%s' % (my_uuid, stack_trace)
        log.error(message)
        end_time = get_local_millisecond_timestamp()
        # performace.insert_performance_log(context_instance=context_instance,
        #                                   phase=PhaseType.ALL.value,
        #                                   status=StatusType.FAILED.value,
        #                                   message=message,
        #                                   start_time=start_time,
        #                                   end_time=end_time)

        return build_error_result(message)


@app.route('/execute/read_big_file', methods=['POST'])
def execute_read_big_file(read_command_json_str = None):
    my_uuid = generate_uuid()
    context_instance = Context()
    # 这个接口专门用于读取大文件，通过在上下文标记为读大文件标志，在后面执行时，可以做相应大文件处理
    context_instance.set('[READ_BIG_FILE_FLAG]', True)

    # if read_command_json_str is None:
    #     read_command = request.get_json()
    # else:
    #     # 把 JSON 字符串转换回 Python 对象
    #     read_command = json.loads(read_command_json_str)

    # read_command_json_str  = json.dumps(read_command)
    # log.info('UUID: %s,接收到读数请求,读数指令read_command是: %s', my_uuid, read_command_json_str)
    read_command = request.get_json()
    # 获取当前进程号
    process_id = os.getpid()
    # 获取当前线程号
    thread_id = threading.current_thread().ident
    parent_uuid = read_command.get('parentUuid')

    log.info('UUID: %s, 父UUID: %s, execute_read_big_file 接收到读数请求,读数指令read_command是: %s,进程ID：%s,线程ID：%s',
             my_uuid,parent_uuid, read_command, process_id, thread_id)
    file_path_and_name = read_command.get('filePathAndName')

    read_rule = read_command.get('readRule')
    interface_id = read_command['interfaceId']
    interface_name = read_command.get('interfaceName')
    invoke_mode = read_command.get('invokeMode')
    need_rate_limit_control = read_command.get('needRateLimitControl')
    fund_id = read_command.get('fundId')
    fund_code = read_command.get('fundCode')
    business_date = read_command['businessDate']
    flow_node_list = read_rule['flowNodeList']


    context_instance.set('[FUND_ID]', fund_id)
    context_instance.set('[FUND_CODE]', fund_code)
    context_instance.set('[BUSINESS_DATE]', business_date)
    context_instance.set('[INTERFACE_ID]', interface_id)
    context_instance.set('[INTERFACE_NAME]', interface_name)
    context_instance.set('[FILE_PATH_AND_NAME]', file_path_and_name)
    context_instance.set('[INVOKE_MODE]', invoke_mode)
    context_instance.set('[UUID]', my_uuid)



    start_time = get_local_millisecond_timestamp()

    # ---------start

    # ---------end
    try:
        # 根据外部传入的限流配置，决定是否进行限流,need_rate_limit_control为1时，表示需要限流,为2时表示不需要限流
        if need_rate_limit_control is not None and need_rate_limit_control == 1:
            api_limit_call()
        if need_rate_limit_control is None:
            api_limit_call()

        for flow_node in flow_node_list:
            file_type = flow_node.get('fileFmt')
            move_data(file_type, file_path_and_name, flow_node, context_instance)

        data_list = context_instance.get('[__DATA_LIST__]')
        field_name_list = context_instance.get('[__FIELD_NAME_LIST__]')
        read_data = {"dataList": data_list, "fieldNameList": field_name_list}

        end_time = get_local_millisecond_timestamp()
        # performace.insert_performance_log(context_instance=context_instance,
        #                                   phase=PhaseType.ALL.value,
        #                                   status=StatusType.SUCCESS.value,
        #                                   message="success",
        #                                   start_time=start_time,
        #                                   end_time=end_time)
        log.info('UUID: %s,父UUID: %s,execute_read_big_file 读数请求处理成功,总体耗时：%s ms', my_uuid, parent_uuid, end_time-start_time)
        return build_success_result(read_data)
    except RateLimitException as e:
        message = 'uuid:%s,execute_read_big_file 发生限流,读数请求处理失败,异常信息：%s' % (my_uuid, 'access limit is exceeded.')
        log.error(message)
        end_time = get_local_millisecond_timestamp()
        # performace.insert_performance_log(context_instance=context_instance,
        #                                   phase=PhaseType.ALL.value,
        #                                   status=StatusType.FAILED.value,
        #                                   message=message,
        #                                   start_time=start_time,
        #                                   end_time=end_time)
        return build_limit_error_result(f'access limit is exceeded.')
    except Exception as e:
        check_logic_result = context_instance.get('check_logic_result')
        if check_logic_result is False:
            check_logic_message = context_instance.get('check_logic_message')
            message = 'uuid:%s,execute_read_big_file 检查逻辑检查不通过,详细信息是:%s' % (my_uuid, check_logic_message)
        else:
            stack_trace = traceback.format_exc()
            if 'resource busy' in stack_trace:
                stack_trace = '文件正在被其他进程占用，请稍后再试。'
            message = 'uuid:%s,读数请求处理失败,异常信息：%s' % (my_uuid, stack_trace)
        log.error(message)
        end_time = get_local_millisecond_timestamp()
        # performace.insert_performance_log(context_instance=context_instance,
        #                                   phase=PhaseType.ALL.value,
        #                                   status=StatusType.FAILED.value,
        #                                   message=message,
        #                                   start_time=start_time,
        #                                   end_time=end_time)

        return build_error_result(message)


def build_success_result(data=None):
    result = {"code": 200, "msg": 'success'}
    if data is not None:
        result["data"] = data  # 如果有数据，添加到结果字典中
    return result


def build_error_result(message=None):
    result = {"code": -500, "msg": message}
    return result

def build_limit_error_result(message=None):
    result = {"code": -429, "msg": message}
    return result


def generate_uuid():
    # 生成一个UUID
    my_uuid = uuid.uuid4()
    my_uuid = str(my_uuid)
    return my_uuid


def get_local_millisecond_timestamp():
    return int(time.time() * 1000)


# 限制函数每分钟最多调用 N 次
CALLS = config.get_config_value("limit.calls")
PERIOD = config.get_config_value("limit.period")


@limits(calls=CALLS, period=PERIOD)
def api_limit_call():
    # 获取当前进程号
    process_id = os.getpid()
    # 获取当前线程号
    thread_id = threading.current_thread().ident

    log.info('[进程ID:%s,线程ID:%s] api_limit_call执行,限流探针......', thread_id, process_id)
    return True


if __name__ == '__main__':

    port = config.get_config_value("server.port")
    threads = config.get_config_value("server.threads")
    log.info('读数工具启动成功,监听端口：%s，线程数：%s', port, threads)
    # app.run(host='0.0.0.0', port=80)
    serve(app, host='0.0.0.0', port=port, threads=threads)

