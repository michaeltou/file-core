import pandas as pd


seperator = "|"
header = None
skip_rows = 12
names = ['F'+str(i) for i in range(1,12)]
names.insert(0, 'column1')
names.insert(1, 'column2')


"""默认读数 sheet1 """
mytxt = pd.read_csv('20180302BOND_VALUATION.txt', sep="|", header=None, skiprows=12, names=names, index_col=False)
# mytxt = pd.read_csv('20180302BOND_VALUATION.txt', sep="|", header=None, skiprows=12, names=names, index_col=False)

print(mytxt)

df = mytxt

