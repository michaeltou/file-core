import pandas as pd
s = pd.Series(["0.006277431666386035"])
print(s.iloc[0])
s2 = pd.to_numeric(s)
print(s2.iloc[0])