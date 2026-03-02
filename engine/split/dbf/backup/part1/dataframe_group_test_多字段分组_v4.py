
from simpledbfdm import Dbf5
from engine.core.migrate_core_engine import *
from engine.db.oracle_read_tool_db_util import execute_dml_sql, execute_query_sql
from engine.core.context import *
from engine.util.sql.SqlUtil import replace_sql
import dbf


def execute_get_belong_sql(sql, context_instance):
    # 将[变量名称] 替换为 :变量名称
    final_sql = replace_sql(sql, context_instance)
    # param_dict是个字典，里面包含了所有变量和参数，刚好可以传给sql语句
    params = context_instance.gen_simple_context_dict()
    # 执行sql语句
    df = execute_query_sql(final_sql, params)
    return df


# 如果不存在，则创建相同结构的空DBF文件
def create_empty_dbf_file_if_not_exist(src_file, dst_file):
    # 判断文件是否存在
    if os.path.exists(dst_file):
        print(f"文件 {dst_file} 存在。")
        return
    # 如果文件不存在，则创建空文件
    with dbf.Table(src_file) as src:
        src.open()
        dst = src.new(dst_file)
        dst.open()
        # do something
        dst.close()

if __name__ == "__main__":


    file_path_and_name = "/Users/douming/Documents/采集发布/测试文件/SJSMX11204.DBF"
    # todo 获取文件名
    source_file_name = os.path.basename(file_path_and_name)
    print(f"来源文件名是: {source_file_name}")

     # todo 获取分组字段列表
    group_list = ['MXZQZH']
    # sql = 'SELECT b.fund_id,b.fund_code,b.fund_name FROM TF_Shareholder a,tf_fundinfo b WHERE a.fund_id = b.fund_id AND a.shareholder_code = :MXZQZH'

    # todo 获取sql语句
    # sql = "SELECT '0899099931' as fund_id from dual"
    sql = "SELECT '0899099931' as fund_id from dual union all SELECT '0899098642' as fund_id from dual "

    my_dbf = Dbf5(file_path_and_name, codec='gbk')
    for chunk in my_dbf.to_dataframe(chunksize=100000):
        # 根据分组列的列表，进行分组，支持多个字段进行分组。 例如：['Name', 'Age']
        grouped_chunk = chunk.groupby(group_list)

        grouped_df_dict = {}
        # 这里的group_tuple_name是一个tuple，表示分组的字段值，例如（'张三', '25'）
        for group_tuple_name, group_df_item in grouped_chunk:
            # 构造一个分组号的dataframe字段，key为字段名称，value为dataframe
            grouped_df_dict[group_tuple_name] = group_df_item

        print(f"分组字段：{group_list}，分组数量：{len(grouped_df_dict)}")

        context_instance = Context()

        final_group_df_dict = {}
        ''' 
          遍历分组的dataframe=grouped_df_dict字典,进行处理，生成最终的dataframe=final_group_df_dict。
         grouped_df_dict里面的个数会和final_group_df_dict的个数会不一样，
         因为有些分组的dataframe有相同的归属，就需要进行合并。
        '''
        for group_tuple_name, group_df_item in grouped_df_dict.items():
            '''
            从group_list 和group_tuple_name 组成一个新的dict，作为上下文参数
            group_list 举例： ['name', 'age']， 
            group_tuple_name 举例：('张三', '25')
            dict(zip(group_list, group_tuple_name)) 后结果为 {'name': '张三', 'age': '25'}
            '''
            result_dict = dict(zip(group_list, group_tuple_name))
            for key, value in result_dict.items():
                context_instance.set(key, value)

            # 根据分组的字段值，执行sql，获取归属。
            belong_df = execute_get_belong_sql(sql, context_instance)
            record_count = len(belong_df)

            #  1、获取到一个归属 ，正常处理
            if record_count == 1:
                # 默认第一列为归属字段，由于这里是只有一条记录，所以取第一行第一列即可
                belong_value = belong_df.iat[0, 0]
                previous_group_df_item = final_group_df_dict.get(belong_value)
                # 使用 concat 函数进行拼接,即：将当前分组的dataframe与之前的dataframe（同归属，即belong_value相同的情况）进行拼接。
                # 最终拆分，是根据final_group_df_dict 的key值进行拆分的。
                concat_group_df = pd.concat([previous_group_df_item, group_df_item], ignore_index=True)
                final_group_df_dict[belong_value] = concat_group_df
            #  2、获取不到归属，把这类数据统一放到无归属的dataframe中，同时记录警告（这个最终根据是否有记录，仅记录一条警告）
            elif record_count == 0:
                previous_group_df_item = final_group_df_dict.get('belong_not_found')
                concat_group_df = pd.concat([previous_group_df_item, group_df_item], ignore_index=True)
                final_group_df_dict['belong_not_found'] = concat_group_df
            #  3、获取到多个归属，拆分为多个归属文件，同时记录警告（这个最终根据是否有记录，仅记录一条警告）
            elif record_count > 1:
                # 获取第一列的列名
                first_column_name = belong_df.columns[0]
                # 获取第一列的列值 转成list
                belong_value_list = belong_df[first_column_name].tolist()
                for belong_value in belong_value_list:
                    previous_group_df_item = final_group_df_dict.get(belong_value)
                    # 使用 concat 函数进行拼接,即：将当前分组的dataframe与之前的dataframe（同归属，即belong_value相同的情况）进行拼接。
                    # 最终拆分，是根据final_group_df_dict 的key值进行拆分的。
                    concat_group_df = pd.concat([previous_group_df_item, group_df_item], ignore_index=True)
                    final_group_df_dict[belong_value] = concat_group_df
            # 其他情况，无需处理
            else:
                pass

        # end of chunk

        # 遍历final_group_df_dict，写入dbf文件
        for belong_value, group_df_item in final_group_df_dict.items():

            group_df_item = group_df_item.replace({'nan': None})
            group_df_item = group_df_item.replace({'None': None})
            group_df_item = group_df_item.replace({np.nan: None})

            # todo 获取目标文件路径 & 并做上下文替换
            dest_file_path = "/Users/douming/Documents/采集发布/测试文件"
            # todo 获取目标文件名 & 并做上下文替换
            dest_file_name = source_file_name + "_" + belong_value+".DBF"

            # 构造文件名
            dest_file_path_and_name = os.path.join(dest_file_path, dest_file_name)

            # 如果文件不存在，则创建空文件
            create_empty_dbf_file_if_not_exist(file_path_and_name, dest_file_path_and_name)
            print(f"开始写入文件 {dest_file_path_and_name} .....")
            start_time = time.time()
            # 写入文件
            dest_table = dbf.Table(dest_file_path_and_name)
            records = []
            try:
                dest_table.open(mode=dbf.READ_WRITE)
                # 写入数据
                # for index, row in group_df_item.iterrows():
                #     desc.append(tuple(row))

                # 使用 itertuples() 快速遍历 DataFrame
                for row in group_df_item.itertuples(index=False):
                    dest_table.append(row)

                # for row in group_df_item.values:
                #     dest_table.append(tuple(row))

            except Exception as e:
                print(f"写入文件 {dest_file_path_and_name} 失败。失败原因：{e}")
            finally:
                # 关闭文件
                dest_table.close()

            print(f"写入文件 {dest_file_path_and_name} 完成。耗时 {time.time() - start_time} 秒。")







