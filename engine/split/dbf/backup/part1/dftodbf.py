# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 15:45:22 2019

@author: vane
"""

import struct
import datetime
import pandas as pd
from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_datetime64_dtype
from pandas.api.types import is_bool_dtype
from pandas.api.types import is_float_dtype
from io import BytesIO
import time


def dbfwrite(df, dbffile):  # df: dataframe; filename: dbffilename
    # createdbffile
    f = open(dbffile, 'wb')
    file = BytesIO()

    my_encoding = 'utf-8'
    # df col&row number
    rownum = df.shape[0]
    colnum = df.shape[1]

    # field
    fieldname = df.columns.values
    fieldspecs = []
    for name in df.columns.values:
        if is_numeric_dtype(df[name]):
            typ = 'N'
            siz = max(list(df[name].apply(str).apply(len)))
            if is_float_dtype(df[name]):
                d = df[name].apply(lambda x: len(str(x).split('.')[1]))
                deci = max(d)
            else:
                deci = 0
            df[name] = df[name].apply(lambda x: str(x).rjust(siz, ' '))
        elif is_datetime64_dtype(df[name]):
            typ = 'D'
            siz = max(list(df[name].apply(str).apply(len)))
            deci = 0
            df[name] = df[name].apply(lambda x: x.strftime('%Y%m%d'))
        elif is_bool_dtype(df[name]):
            typ = 'L'
            siz = max(list(df[name].apply(str).apply(len)))
            deci = 0
            df[name] = df[name].apply(lambda x: str(x)[0].upper())
        else:
            siz = max(list(df[name].apply(str).apply(len)))
            if siz > 255:
                typ = 'M'
            else:
                typ = 'C'
            deci = 0
            df[name] = df[name].apply(lambda x: str(x)[:siz].ljust(siz, ' '))
        fieldinfo = (typ, siz, deci)
        fieldspecs.append(fieldinfo)

    # dbf header info
    version = 3
    now = datetime.datetime.now()
    year = now.year - 1900
    month = now.month
    day = now.day
    recordnum = rownum
    headerlen = colnum * 32 + 33
    recordlen = sum(field[1] for field in fieldspecs) + 1
    hdr = struct.pack('<BBBBLHH20x', version, year, month, day, recordnum, headerlen, recordlen)
    file.write(hdr)


    # write field into dbf
    for name, (typ, size, deci) in zip(fieldname, fieldspecs):
        name = name.ljust(11, '\x00')
        fld = struct.pack('<11sc4xBB14x', bytes(str(name).encode(my_encoding)), bytes(typ.encode(my_encoding)), size, deci)
        file.write(fld)
    n = '\r'
    file.write(bytes(str(n).encode(my_encoding)))
    start_time = time.time()
    # records
    for i in range(0, rownum):
        n = ' '
        file.write(bytes(str(n).encode(my_encoding)))
        for j in range(0, colnum):
            value = df.iloc[i, j]
            file.write(bytes(str(value).encode(my_encoding)))
        if i % 10000 == 0:
            print(f"已处理 {i} 条记录,耗时 {time.time() - start_time} 秒。")
            start_time = time.time()



    # end of file
    n = '\x1A'
    file.write(bytes(str(n).encode(my_encoding)))
    f.write(file.getvalue())
    # close file
    f.flush()
    f.close()
    print("Success!")

