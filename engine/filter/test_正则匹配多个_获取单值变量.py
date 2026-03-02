import re


def get_string_by_regex(text, pattern):
    matches = re.findall(pattern, text)
    if matches:
        print("Match found:", matches)
        return matches
    else:
        print("No match found.")
        return None


# 使用例子
# txt = 'HQZRSP >= [[MY_LIST.HQZRSP]] and HQJRKP >= [[MY_LIST.HQJRKP]]'
text = ('HQZRSP >= [[MY_LIST.HQZRSP]] and HQJRKP >= [[MY_LIST.HQJRKP]]'
        ' AND FUND_ID = [FUND_ID] AND D_RQ = [BUSINESS_DATE]')
# txt = '  FUND_ID = [FUND_ID]'
pattern = r'[^\[]\[{1}([\w.]+)\]{1}'
result = get_string_by_regex(text, pattern)
print(result)



replace_text = text.replace('[FUND_ID]', str(2122))
print(replace_text)

