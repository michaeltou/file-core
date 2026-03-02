import pandas as pd
from datetime import datetime

date_str = '9999-12-31'
date_obj = datetime.strptime(date_str, '%Y-%m-%d')
date_series = pd.Series([date_obj])
print(date_series)