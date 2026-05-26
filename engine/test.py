import pandas as pd
import engine.util.log as log

#构造一个dataframe ，并且打印出它的内容
df = pd.DataFrame({
    'ID': [1, 2, 3],
    'NAME': ['Alice', 'Bob', 'Charlie'],
    'AGE': ['25', '30', '35']
})

log.info('df的内容是：%s', df)


df = df.query("AGE.astype('int') > 30")



print(df)


