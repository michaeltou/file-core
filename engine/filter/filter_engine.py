import re
import pandas as pd
from datetime import datetime


def convert_date_format(date_str, from_format='%Y%m%d', target_format='%Y-%m-%d'):
    # 将字符串转换为日期对象
    date_obj = datetime.strptime(date_str, from_format)
    # 格式化日期对象为目标字符串格式
    formatted_date_str = date_obj.strftime(target_format)
    return formatted_date_str

class FilterEngine:
    def __init__(self):
        pass

    @staticmethod
    def process_filter(df, filter_logic, context_instance):
        result_df = pd.DataFrame()
        if filter_logic is None or filter_logic.strip() == '':
            result_df = df
            return result_df
        """ 
        # 过滤逻辑编写例子，  注释这行:
         filter_logic = 'HQZRSP >= [[MY_LIST.HQZRSP]] & HQJRKP >= [[MY_LIST.HQJRKP]] & HQCJJE == [HQCJJE]'

        # 执行sql，获取到数据， 调用执行sql获取数据(在执行sql节点会执行这个逻辑) start
        my_list = [
            {'HQZRSP': 2.09, 'HQJRKP': 2.09},
            {'HQZRSP': 0.1, 'HQJRKP': 0.2}
        ]
        # 放入到上下文中
        context_instance.set('[[MY_LIST]]', my_list)

        context_instance.set('[HQCJJE]', 12331)
        """
        #  调用执行sql获取数据(在执行sql节点会执行这个逻辑) end

        # 1 把单值变量全部替换成上下文的变量（先后顺序很重要，不能颠倒：先单值变量，后数据集变量）
        used_simple_param_list = FilterEngine.get_used_simple_param_list(filter_logic)
        if used_simple_param_list:
            for simple_param in used_simple_param_list:
                simple_param_key = '[' + simple_param + ']'
                simple_param_value = context_instance.get(simple_param_key)
                filter_logic = filter_logic.replace(simple_param_key, str(simple_param_value))

        # 2 把数据集变量替换成上下文的变量（先后顺序很重要，不能颠倒：先单值变量，后数据集变量）
        # 返回值举例：used_cursor_param_list =['MY_LIST.HQZRSP', 'MY_LIST.HQJRKP']
        used_cursor_param_list = FilterEngine.get_used_cursor_param_list(filter_logic)
        if used_cursor_param_list:
            """
              数据集变量使用场景：
                1 多产品数据合并在一个文件中的场景，首先根据产品Z的一些附加属性，执行sql获取数据,找出对应的关联数据MY_LIST，
                    这个关联数据MY_LIST是个数据集（这个数据集会有多条记录，每条记录中有A字段，B字段）。
                2 然后文件中的多个字段，比如C字段、D字段，需要同时满足 C字段 == [[MY_LIST.A字段]] & D字段 == [[MY_LIST.B字段]] 就是属于这个产品Z的数据。
                    由于MY_LIST是多条记录，只要文件中的字段满足MY_LIST中的一条记录，就算满足条件，然后把结果合并即为这个产品关联的所有数据。
                举例：
                输入：
                    关联数据MY_LIST = [{'HQZRSP': 0.1, 'HQJRKP': 0.2}, {'HQZRSP': 0.3, 'HQJRKP': 0.4}]
                    过滤写法： HQZRSP >= [[MY_LIST.HQZRSP]] & HQJRKP >= [[MY_LIST.HQJRKP]]
                执行过程：文件加载为dataframe后，执行过滤条件 HQZRSP >= 0.1 & HQJRKP >= 0.2 获取过滤的数据dataframe_1,
                        再执行过滤条件 HQZRSP >= 0.3 & HQJRKP >= 0.4 获取过滤的数据dataframe_2,
                输出：
                    dataframe_1和dataframe_2合并即为这个产品关联的所有数据。
            """


            # 举例:cursor_param_name= 'MY_LIST'
            cursor_param_name = FilterEngine.get_cursor_param_name(used_cursor_param_list)
            # 举例:cursor_param_name_key = '[[MY_LIST]]'
            cursor_param_name_key = '[[' + cursor_param_name + ']]'
            # 举例:cursor_param_data = [{'HQZRSP': 2.09, 'HQJRKP': 2.09}, {'HQZRSP': 0.1, 'HQJRKP': 0.2}]
            cursor_param_data = context_instance.get(cursor_param_name_key)  # 从上下文中获取数据集变量数据
            if cursor_param_data:
                # 合并过滤后的结果
                combined_df = pd.DataFrame()
                # 遍历游标数据,对每行数据进行过滤（上下文数据集数据的每一行进行一次过滤，然后再合并）
                for cursor_data_item in cursor_param_data:
                    filtered_part_df = pd.DataFrame()
                    filter_logic_for_one_row = filter_logic
                    # 处理一行数据 开始
                    # 举例：used_cursor_param_list =['MY_LIST.HQZRSP', 'MY_LIST.HQJRKP']
                    # 遍历过滤条件中的变量 used_cursor_param_item ='MY_LIST.HQZRSP'
                    for used_cursor_param_item in used_cursor_param_list:
                        # 举例：used_cursor_param_item_str = '[[MY_LIST.HQZRSP]]'
                        used_cursor_param_item_str = '[[' + used_cursor_param_item + ']]'
                        # 数据集变量的属性名称  'MY_LIST.HQZRSP' -> 'HQZRSP'， used_cursor_param_item_name = 'HQZRSP'
                        used_cursor_param_item_name = used_cursor_param_item.split('.')[1]
                        # 替换变量  HQZRSP >= [[MY_LIST.HQZRSP]] & HQJRKP >= [[MY_LIST.HQJRKP]]
                        # 替换为: HQZRSP >= 2.09 & HQJRKP >= 2.09
                        filter_logic_for_one_row = filter_logic_for_one_row.replace(used_cursor_param_item_str,
                                                                                    str(cursor_data_item.get(
                                                                                        used_cursor_param_item_name)))
                    #  处理一行数据 结束

                    # 执行一次过滤
                    filtered_part_df = df.query(filter_logic_for_one_row)
                    # 合并过滤后的结果到combined_df
                    combined_df = pd.concat([combined_df, filtered_part_df], ignore_index=True)

                # 合并后的结果赋值给df
                result_df = combined_df
        else:
            # 执行过滤逻辑
            result_df = df.query(filter_logic)
        return result_df



    @staticmethod
    def get_used_simple_param_list(text):
        """
        获取过滤字符串中为使用了简单变量
        输入 txt = ''HQZRSP >= [[MY_LIST.HQZRSP]] and HQJRKP >= [[MY_LIST.HQJRKP]]'
            ' AND FUND_ID = [FUND_ID] AND D_RQ = [BUSINESS_DATE]''，
        返回匹配的列表：['FUND_ID', 'BUSINESS_DATE']
        """
        # pattern = r'[^\[]\[{1}([\w.]+)\]{1}'
        pattern = r'[^\[]{0,}\[{1}([\w.]+)\]{1}'
        matches = re.findall(pattern, text)
        if matches:
            # print("Match found:", matches)
            return matches
        else:
            # print("No match found.")
            return None


    @staticmethod
    def get_used_cursor_param_list(text):
        """
        获取过滤字符串中为使用了数据集变量
        输入 txt = 'HQZRSP >= [[MY_LIST.HQZRSP]] and HQJRKP >= [[MY_LIST.HQJRKP]]'，
        返回匹配的列表：['MY_LIST.HQZRSP', 'MY_LIST.HQJRKP']
        """
        pattern = r'\[\[([\w.]+)\]\]'
        matches = re.findall(pattern, text)
        if matches:
            # print("Match found:", matches)
            return matches
        else:
            # print("No match found.")
            return None

    @staticmethod
    def get_cursor_param_name(used_cursor_param_list):
        """
        获取上下文数据集变量的名称，只取第一个即可（原因:实际在过滤条件中，只会有一个列表变量，不能有多个数据集变量）。
        :param used_cursor_param_list: 举例：['MY_LIST.HQZRSP', 'MY_LIST.HQJRKP']
        :return: 举例：'MY_LIST'
        """
        if used_cursor_param_list:
            # 取第一个元素，例如：'MY_LIST.HQZRSP'
            first_item = used_cursor_param_list[0]
            # 取第一个元素的前缀，例如：'MY_LIST'
            first_item_param_name = first_item.split('.')[0]
            return first_item_param_name
        else:
            return None

