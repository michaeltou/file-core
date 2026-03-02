from openpyxl.compat import deprecated

from engine.core.context import *
import re

# 这里的sql字符串里面是带有[]的变量， 替换成实际的:变量名称的字符串。
# 例如 sql =  SELECT * FROM MY_TEST_TABLE WHERE name = [NAME] AND age = [AGE]
# 替换成:sql =  SELECT * FROM MY_TEST_TABLE WHERE name = :NAME AND age = :AGE


def replace_sql(sql, context_instance):
    sql = replace_sql_for_pure_str_replace(sql, context_instance)
    simple_params_dict = context_instance.gen_simple_context_dict()
    for key, value in simple_params_dict.items():
        new_key = '[' + key + ']'
        sql_key = ':' + key
        sql = sql.replace(new_key, sql_key)
    return sql

"""
这里实现的是sql字符串的替换，而是直接替换成字符串， 而不是使用sql占位符的替换。

如果sql 中如果有 PURE_STR_REPLACE 字符串，则做个定制化替换 
例如[JJDM] 变量的值为 '10001','10002','10003',
该函数的作用是把 PURE_STR_REPLACE([JJDM]) 替换为 字符串 '10001','10002','10003' 

原始的 sql =  SELECT * FROM MY_TEST_TABLE WHERE name = IN (PURE_STR_REPLACE([JJDM]))
替换成:sql =  SELECT * FROM MY_TEST_TABLE WHERE name = IN ('10001','10002','10003')

"""
def replace_sql_for_pure_str_replace(sql, context_instance):
    if 'PURE_STR_REPLACE' not in sql:
        return sql

    # 使用正则，找到sql中所有的PURE_STR_REPLACE([JJDM])格式的字符串
    # 找到所有的PURE_STR_REPLACE([JJDM]) 格式的字符串
    pattern = r'PURE_STR_REPLACE\([^\)]+\)'
    matches = re.findall(pattern, sql)
    if matches:
        for match in matches:
            # match的值为："PURE_STR_REPLACE([JJDM])"

            # 获取到上下文变量列表['JJDM']的值
            used_simple_param_list = get_used_simple_param_list(match)
            if used_simple_param_list:
                # 获取第一个值
                simple_param_key = '[' + used_simple_param_list[0] + ']'
                simple_param_value = context_instance.get(simple_param_key)

            # 替换sql
            # new_sql = sql[:start_index] + simple_param_value + sql[end_index+1:]

            sql = sql.replace(match, simple_param_value)
            # print(sql)
    return sql





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

def test_replace_sql_with_list():
    sql = "SELECT * FROM MY_TEST_TABLE WHERE name = IN (PURE_STR_REPLACE([JJDM]))"
    context_instance = Context()
    context_instance.set('[JJDM]', "'10001','10002','10003'")
    replace_sql_for_pure_str_replace(sql, context_instance)



def test_replace_sql():
    sql = "SELECT * FROM MY_TEST_TABLE WHERE name = [NAME] AND age = [AGE] and age2 = [AGE]"
    context_instance = Context()
    context_instance.set('[NAME]', 'Tom2')
    context_instance.set('[AGE]', 252)
    replaced_sql = replace_sql(sql, context_instance)
    print(replaced_sql)

if __name__ == '__main__':
    test_replace_sql_with_list()