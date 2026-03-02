import re

def get_used_simple_param_list_test():
    """
    获取过滤字符串中为使用了简单变量
    输入 txt = ''HQZRSP >= [[MY_LIST.HQZRSP]] and HQJRKP >= [[MY_LIST.HQJRKP]]'
        ' AND FUND_ID = [FUND_ID] AND D_RQ = [BUSINESS_DATE]''，
    返回匹配的列表：['FUND_ID', 'BUSINESS_DATE']
    """
    txt = ''' HQZRSP >= [[MY_LIST.HQZRSP]] and HQJRKP >= [[MY_LIST.HQJRKP]]
     AND FUND_ID = [FUND_ID] AND D_RQ = [BUSINESS_DATE]'''
    pattern = r'[^\[]\[{1}([\w.]+)\]{1}'
    matches = re.findall(pattern, txt)
    if matches:
        # print("Match found:", matches)
        return matches
    else:
        # print("No match found.")
        return None

def get_used_simple_param_list_test2():
        """
        获取过滤字符串中为使用了简单变量
        输入 txt = ''HQZRSP >= [[MY_LIST.HQZRSP]] and HQJRKP >= [[MY_LIST.HQJRKP]]'
            ' AND FUND_ID = [FUND_ID] AND D_RQ = [BUSINESS_DATE]''，
        返回匹配的列表：['FUND_ID', 'BUSINESS_DATE']
        """
        txt = ''' df['F[ZHH]'] = df['F[ZHH]'] + 1 '''
        pattern = r'[^\[]\[{1}([\w.]+)\]{1}'
        matches = re.findall(pattern, txt)
        if matches:
            # print("Match found:", matches)
            return matches
        else:
            # print("No match found.")
            return None

if __name__ == '__main__':
    matches = get_used_simple_param_list_test2()
    print(matches)