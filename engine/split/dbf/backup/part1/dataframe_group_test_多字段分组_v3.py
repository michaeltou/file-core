import pandas as pd

if __name__ == '__main__':
    # 创建一个示例 DataFrame
    data = {
        'Name': ['Alice', 'Bob', 'Alice', 'Bob', 'Alice'],
        'Subject': ['Math', 'Math', 'English', 'English', 'Math'],
        'Score': [85, 90, 78, 88, 92]
    }
    df = pd.DataFrame(data)

    # 根据 'Name' 和 'Subject' 列进行分组
    grouped = df.groupby(['Name', 'Subject'])

    # 遍历分组对象，将每一组转换为独立的 DataFrame
    grouped_dfs = {}
    for name, group in grouped:
        grouped_dfs[name] = group

    # 打印每个分组的 DataFrame
    for name, group_df in grouped_dfs.items():
        print(f"Group: {name}")
        print(group_df)
        print()
