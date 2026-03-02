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
text = 'HQZRSP >= [[MY_LIST.HQZRSP]] and HQJRKP >= [[MY_LIST.HQJRKP]]'
# txt = 'HQZRSP >= [[MY_LIST.HQZRSP]] and HQJRKP >= [[MY_LIST.HQJRKP]] AND FUND_ID = [FUND_ID]'
# txt = '  FUND_ID = [FUND_ID]'
pattern = r'\[\[([\w.]+)\]\]'
result = get_string_by_regex(text, pattern)
print(result)



