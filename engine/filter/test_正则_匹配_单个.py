import re

def get_string_by_regex(text, pattern):
    match = re.search(pattern, text)
    if match:
        # 使用捕获组来获取匹配的特定部分
        captured_group = match.group(1)
        print("Match found:", captured_group)
        return captured_group
    else:
        print("No match found.")
        return None

# 使用例子
text = 'HQZRSP >= [[MY_LIST.HQZRSP]] and HQJRKP >= [[MY_LIST.HQJRKP]]'

# 使用捕获组来匹配方括号内的内容
pattern = r'\[\[([\w.]+)\]\]'
result = get_string_by_regex(text, pattern)
print(result)  # 输出: MY_LIST.HQZRSP