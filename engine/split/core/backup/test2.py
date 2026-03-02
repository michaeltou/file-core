
import pandas as pd
if __name__ == '__main__':
    # 构造示例数据
    data = {
        "column1": ["ZJZH1_ZJZH2", "ZJZH3_ZJZH4", "ZJZH5_ZJZH6"],
        "product_id": ["产品ID1", "产品ID2", "产品ID3"]
    }

    # 创建 DataFrame
    one_batch_belong_df = pd.DataFrame(data)

    # ... existing code ...
    # 假设 search_key 是你要搜索的值
    search_key = "ZJZH3_ZJZH4"

    # 获取第一列和第二列的列名
    first_col_name = one_batch_belong_df.columns[0]
    second_col_name = one_batch_belong_df.columns[1]

    # 使用 query 方法筛选数据
    filtered_df = one_batch_belong_df.query(f"{first_col_name} == @search_key")

    # 提取第二列数据构造新的 DataFrame
    new_df = filtered_df[[second_col_name]].copy()


    print(new_df)