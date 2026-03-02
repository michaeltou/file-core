import dbf


if __name__ == '__main__':

    srcfile = "/Users/douming/Documents/采集发布/测试文件/SJSMX11204.DBF"

    dstfile = './new_target.dbf'


    with dbf.Table(srcfile) as src:
        src.open()

        dst = src.new(dstfile)

        dst.open()

        # do something

        dst.close()