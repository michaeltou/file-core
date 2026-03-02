from engine.cnst.CheckLogicSwith import CheckLogicSwitch
from engine.filter.filter_engine import FilterEngine
from datetime import datetime
import pandas as pd

def convert_date_format(date_str, from_format='%Y%m%d', target_format='%Y-%m-%d'):
    # 将字符串转换为日期对象
    date_obj = datetime.strptime(date_str, from_format)
    # 格式化日期对象为目标字符串格式
    formatted_date_str = date_obj.strftime(target_format)
    return formatted_date_str


def check_file(flow_node_config,df, context_instance):
    check_logic_switch = flow_node_config.get('checkLogicSwitch')
    # 如果没有配置checkLogicSwitch，则不进行检查
    if not check_logic_switch:
        return
    if check_logic_switch == CheckLogicSwitch.ON.value:
        check_logic = flow_node_config.get('checkLogic')

        # 把check_logic中的变量替换成上下文的变量. 例如 df['F[JE]'] = df['F[JE]'] + 1 转成 df['F2'] = df['F2'] + 1
        used_param_list_in_check_logic = FilterEngine.get_used_simple_param_list(check_logic)
        if used_param_list_in_check_logic:
            for param_item in used_param_list_in_check_logic:
                context_param_key = '[' + param_item + ']'
                context_param_value = context_instance.get(context_param_key)
                check_logic = check_logic.replace(context_param_key, str(context_param_value))

        check_logic_message = flow_node_config.get('checkLogicMessage')
        my_checked_dataframe = df.query(check_logic)
        # 过滤出，发现没有满足条件的行，说明没有问题
        if my_checked_dataframe.shape[0] == 0:
            pass
        else:  # 发现有满足条件的行，说明有问题
            used_simple_param_list = FilterEngine.get_used_simple_param_list(check_logic_message)
            # 替换掉简单参数, 并抛出异常
            if used_simple_param_list:
                for simple_param in used_simple_param_list:
                    simple_param_key = '[' + simple_param + ']'
                    simple_param_value = context_instance.get(simple_param_key)
                    check_logic_message = check_logic_message.replace(simple_param_key, str(simple_param_value))
                    context_instance.set('check_logic_message', check_logic_message)
                    context_instance.set('check_logic_result', False)
                    raise Exception(check_logic_message)
            else:  # 没有简单参数，直接抛出异常
                context_instance.set('check_logic_message', check_logic_message)
                context_instance.set('check_logic_result', False)
                raise Exception(check_logic_message)
    else:  # 如果checkLogicSwitch配置为OFF，则不进行检查
        pass



