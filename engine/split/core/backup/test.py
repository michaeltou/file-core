

import pandas as pd

if __name__ == '__main__':
    # 创建一个示例DataFrame
    data = {
        'Clientid': ['北京', '上海', '广州', '北京', '上海', '广州'],
        'Month': ['1月', '1月', '1月', '2月', '2月', '2月'],
        'Sales': [100, 150, 200, 120, 180, 210]
    }
    df = pd.DataFrame(data)


    grouped_chunk = df.groupby(['clientID'])


    for group_field_name_tuple_value, group_df_item in grouped_chunk:
        print(group_field_name_tuple_value)
        print(group_df_item)