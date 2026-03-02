from engine.cnst.CheckLogicSwith import CheckLogicSwitch
from engine.filter.filter_engine import FilterEngine
from engine.core.context import *


def check_node(flow_node, context_instance):
    """
    根据 flow_node 的配置，校验流程节点
    :param flow_node:
    :param context_instance:
    :return:
    """
    flow_node_check_config = flow_node.get('flowNodeCheckConfig')
    if flow_node_check_config is None:
        return

    check_logic = flow_node_check_config.get('checkLogic')
    if check_logic is None:
        return True



    # 把check_logic中的变量替换成实际值
    check_logic_param_list = FilterEngine.get_used_simple_param_list(check_logic)
    if check_logic_param_list:
        for simple_param in check_logic_param_list:
            simple_param_key = '[' + simple_param + ']'
            simple_param_value = context_instance.get(simple_param_key)
            check_logic = check_logic.replace(simple_param_key, str(simple_param_value))

    check_logic_str = 'execute_result = (' + check_logic + ')'
    # 创建一个空字典用于存储局部变量
    result_dict = {}
    exec(check_logic_str, globals(), result_dict)
    result = result_dict.get('execute_result')

    # 校验检查条件执行结果为True，则代表不通过检查，报出错误信息
    if result is True:
        check_logic_message = flow_node_check_config.get('checkLogicMessage')
        # 把check_logic_message中的变量替换成实际值
        check_logic_message_param_list = FilterEngine.get_used_simple_param_list(check_logic_message)
        if check_logic_message_param_list:
            for simple_param in check_logic_message_param_list:
                simple_param_key = '[' + simple_param + ']'
                simple_param_value = context_instance.get(simple_param_key)
                check_logic_message = check_logic_message.replace(simple_param_key, str(simple_param_value))

        context_instance.set('check_logic_message', check_logic_message)
        context_instance.set('check_logic_result', False)
        return False
    # 校验检查条件执行结果为False，则代表通过检查，不报出错误信息
    else:
        context_instance.set('check_logic_result', True)
        return True




if __name__ == '__main__':
    flow_node = {
        'flowNodeCheckConfig': {
            'checkLogic': '[C] == 100',
            'checkLogicMessage': '您构造的上下文变量的值C不正确，应为100，但实际只是:[C]'
        }
    }

    context_instance = Context()
    context_instance.set('[C]', 3)
    check_result = check_node(flow_node, context_instance)
    if check_result:
        print('通过')
    else:
        print('不通过')