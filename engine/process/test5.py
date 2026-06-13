import pandas as pd

# 1. 构造样例 DataFrame
df = pd.DataFrame({
    'rate': ['0.006277431666386035', '0.000123456789012345', '0.009876543210987654']
})

# 2. 执行前：字符串类型，精度完整
val_before = df['rate'].iloc[0]
print(f"执行前: type={type(val_before)}, repr={repr(val_before)}")
# 执行前: type=<class 'str'>, repr='0.006277431666386035'

# 3. 执行 pd.to_numeric
from decimal import Decimal

df['rate'] = df['rate'].apply(
    lambda x: Decimal(str(x)) if pd.notna(x) and str(x).strip() != '' else None
)

# 4. 执行后：float64，尾部精度丢失
val_after = df['rate'].iloc[0]
print(f"执行后: type={type(val_after)}, repr={repr(val_after)}")
# 执行后: type=<class 'float'>, repr=0.006277431666386035

# 5. 对比前后差异
print(f"\n原始字符串:  {val_before}")
print(f"转换后float: {val_after}")
print(f"是否相等:    {val_before == str(val_after)}")