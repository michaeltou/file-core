
from simpledbfdm import Dbf5
from engine.core.migrate_core_engine import *
from engine.db.oracle_read_tool_db_util import execute_dml_sql, execute_query_sql
from engine.core.context import *
from engine.util.sql.SqlUtil import replace_sql
import dbf


# 获取某个归属
def execute_get_belong_sql(sql, context_instance):
    # 将[变量名称] 替换为 :变量名称
    final_sql = replace_sql(sql, context_instance)
    # param_dict是个字典，里面包含了所有变量和参数，刚好可以传给sql语句
    params = context_instance.gen_simple_context_dict()
    # 执行sql语句
    df = execute_query_sql(final_sql, params)
    return df


# 获取所有归属
def get_all_belong(get_all_belong_sql):
    params = None
    # 执行sql语句
    df = execute_query_sql(get_all_belong_sql, params)
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


# 写入文件 追加写入
def write_to_file(destination_file_path_and_name, dataframe_for_one_belong):
    if dataframe_for_one_belong is None or dataframe_for_one_belong.empty:
        return

    start_time = time.time()
    '''写入文件
    另外：'cp936'：这是 Windows 系统中用于中文的编码，
    它等同于 GBK 编码。GBK 是在 GB2312 基础上扩展的中文编码，支持更多的中文字符，包括繁体字等。
    在 dbf 库中使用 'cp936' 可以很好地处理中文数据。
    '''
    dest_table = dbf.Table(destination_file_path_and_name, codepage='cp936')
    try:
        dest_table.open(mode=dbf.READ_WRITE)
        # 写入数据
        # for index, row in dataframe_for_one_belong.iterrows():
        #     desc.append(tuple(row))

        # 使用 itertuples() 快速遍历 DataFrame
        for row in dataframe_for_one_belong.itertuples(index=False):
            dest_table.append(row)

        # for row in dataframe_for_one_belong.values:
        #     dest_table.append(tuple(row))

    except Exception as e:
        print(f"写入文件 {destination_file_path_and_name} 失败。失败原因：{e}")
    finally:
        # 关闭文件
        dest_table.close()

    print(f"写入文件 {destination_file_path_and_name} 完成。耗时 {time.time() - start_time} 秒。")

if __name__ == '__main__':

    source_file_path_and_name = "/Users/douming/Documents/采集发布/测试文件/SJSGB1205.DBF"
    # todo 获取文件名
    source_file_name = os.path.basename(source_file_path_and_name)
    print(f"来源文件名是: {source_file_name}")

     # todo 获取分组字段列表
    group_list = ['GBLB']
    # sql = 'SELECT b.fund_id,b.fund_code,b.fund_name FROM TF_Shareholder a,tf_fundinfo b WHERE a.fund_id = b.fund_id AND a.shareholder_code = :MXZQZH'

    # todo 获取sql语句
    sql = "SELECT 'fund_id_1' as fund_id ,'func_code_2' as fund_code  from dual"
    # sql = ("SELECT 'fund_id_1' as fund_id ,'func_code_1' as fund_code from dual union all "
    #        "select 'fund_id_2' as fund_id ,'func_code_2' as fund_code from dual ")
    # sql = "SELECT 'fund_id_1' as fund_id ,'func_code_2' as fund_code  from dual where 1=2"

    my_dbf = Dbf5(source_file_path_and_name, codec='gbk')
    for chunk in my_dbf.to_dataframe(chunksize=100000):
        # 最终的按照归属分组的dataframe字典，key为归属值，value为dataframe格式的记录
        final_df_dict_for_belong = {}

        '''
            使用场景：即每个归属，都有自己的上下文。构造一个以分组为key，value为Context实例的字典。
            目前有的上下文内容包含：BELONG_VALUE(即归属值),归属sql查询的所有值，路径上的[]通配符（to be added)，文件名称上的[]+捕获组（to be added）。
        '''
        context_dict_for_belong = {}
        # 根据分组列的列表，进行分组，支持多个字段进行分组。 例如：['Name', 'Age']
        grouped_chunk = chunk.groupby(group_list)

        grouped_df_dict = {}
        # 这里的group_tuple_name是一个tuple，表示分组的字段值，例如（'张三', '25'）
        for group_tuple_name, group_df_item in grouped_chunk:
            # 构造一个分组号的dataframe字段，key为字段名称，value为dataframe
            grouped_df_dict[group_tuple_name] = group_df_item

        print(f"分组字段：{group_list}，分组数量：{len(grouped_df_dict)}")
        ''' 
          遍历分组的dataframe=grouped_df_dict字典,进行处理，生成最终的dataframe=final_df_dict_for_belong。
         grouped_df_dict里面的个数会和final_df_dict_for_belong的个数会不一样，
         因为有些分组的dataframe有相同的归属，就需要进行合并。
        '''
        for group_tuple_name, group_df_item in grouped_df_dict.items():
            # 分组上下文，仅用于sql执行
            group_context_instance = Context()
            '''
            从group_list 和group_tuple_name 组成一个新的dict，作为上下文参数
            group_list 举例： ['name', 'age']， 
            group_tuple_name 举例：('张三', '25')
            dict(zip(group_list, group_tuple_name)) 后结果为 {'name': '张三', 'age': '25'}
            '''
            result_dict = dict(zip(group_list, group_tuple_name))
            for key, value in result_dict.items():
                group_context_instance.set(key, value)
            # todo 获取归属，1：执行sql 2：字段即归属
            # 根据分组的字段值，执行sql，获取归属。
            belong_df = execute_get_belong_sql(sql, group_context_instance)
            record_count = len(belong_df)

            #  1、获取到一个归属 ，正常处理
            if record_count == 1:
                # 默认第一列为归属字段（todo 加到备注里面），由于这里是只有一条记录，所以取第一行第一列即可
                belong_value = belong_df.iat[0, 0]

                previous_group_df_item = final_df_dict_for_belong.get(belong_value)
                # 使用 concat 函数进行拼接,即：将当前分组的dataframe与之前的dataframe（同归属，即belong_value相同的情况）进行拼接。
                # 最终拆分，是根据final_group_df_dict 的key值进行拆分的。
                concat_group_df = pd.concat([previous_group_df_item, group_df_item], ignore_index=True)
                final_df_dict_for_belong[belong_value] = concat_group_df

                # 构造某个归属的上下文实例 start
                context_instance_for_one_belong = Context()
                context_instance_for_one_belong.set('BELONG_VALUE', belong_value)
                all_column_list = belong_df.columns.tolist()
                # 构造某个分组的上下文实例
                for column_name in all_column_list:
                    column_value = belong_df[column_name].iat[0]  # 因为只有一行记录，所以取第一行即可
                    context_instance_for_one_belong.set(column_name, column_value)
                ''' 
                    key为归属值，value为上下文实例。这个字典context_dict_for_belong会在后续文件拆分时使用。
                '''
                context_dict_for_belong[belong_value] = context_instance_for_one_belong
                # 构造某个归属的上下文实例 end
            #  2、获取不到归属，把这类数据统一放到无归属的dataframe中，同时记录警告（这个最终根据是否有记录，仅记录一条警告）
            elif record_count == 0:
                previous_group_df_item = final_df_dict_for_belong.get('BELONG_NOT_FOUND')
                concat_group_df = pd.concat([previous_group_df_item, group_df_item], ignore_index=True)
                final_df_dict_for_belong['BELONG_NOT_FOUND'] = concat_group_df

                # 构造某个归属的上下文实例 start
                # 无归属的场景，也构造一个分组的上下文实例，并添加到分组上下文字典context_dict_for_belong中
                context_instance_for_one_belong = Context()
                context_instance_for_one_belong.set('BELONG_VALUE', 'BELONG_NOT_FOUND')
                context_dict_for_belong['BELONG_NOT_FOUND'] = context_instance_for_one_belong
                # 构造某个归属的上下文实例 end
            #  3、获取到多个归属，拆分为多个归属文件，同时记录警告（这个最终根据是否有记录，仅记录一条警告）
            elif record_count > 1:
                # 获取第一列的列名（ 默认第一列为归属字段）
                first_column_name = belong_df.columns[0]
                # 获取第一列的列值(即多个归属值) 转成list
                belong_value_list = belong_df[first_column_name].tolist()
                for index, belong_value in enumerate(belong_value_list):
                    previous_group_df_item = final_df_dict_for_belong.get(belong_value)
                    # 使用 concat 函数进行拼接,即：将当前分组的dataframe与之前的dataframe（同归属，即belong_value相同的情况）进行拼接。
                    # 最终拆分，是根据final_group_df_dict 的key值进行拆分的。
                    concat_group_df = pd.concat([previous_group_df_item, group_df_item], ignore_index=True)
                    final_df_dict_for_belong[belong_value] = concat_group_df

                    # 构造某个归属的上下文实例 start
                    context_instance_for_one_belong = Context()
                    context_instance_for_one_belong.set('BELONG_VALUE', belong_value)
                    all_column_list = belong_df.columns.tolist()
                    # 构造某个归属的上下文实例
                    for column_name in all_column_list:
                        column_value = belong_df[column_name].iat[index]
                        context_instance_for_one_belong.set(column_name, column_value)
                    ''' 
                        key为归属值，value为上下文实例。这个字典context_dict_for_belong会在后续文件拆分时使用。
                    '''
                    context_dict_for_belong[belong_value] = context_instance_for_one_belong
                    # 构造某个归属的上下文实例 end

            # 其他情况，无需处理
            else:
                pass

        # end of chunk

        # todo 获取所有的归属(加缓存)  ,举例： select fund_code from tf_fundinfo;
        get_all_belong_sql = "select fund_code from tf_fundinfo"
        all_belong_df = get_all_belong(get_all_belong_sql)
        # 获取第一列的列名（ 默认第一列为归属字段）
        first_column_name = all_belong_df.columns[0]
        # 获取第一列的列值(即多个归属值) 转成list
        all_belong_value_list = all_belong_df[first_column_name].tolist()
        for belong_value in all_belong_value_list:
            if belong_value not in final_df_dict_for_belong:
                final_df_dict_for_belong[belong_value] = pd.DataFrame()

            # 判断belong_value 是否在final_df_dict_for_belong中，
            # 如果不在，则加入一个空的dataframe，后面只需要创建一个空文件即可
            # 如果存在，则不处理



        # 遍历final_group_df_dict，写入dbf文件
        for belong_value, df_for_one_belong in final_df_dict_for_belong.items():
            df_for_one_belong = df_for_one_belong.replace({'nan': None})
            df_for_one_belong = df_for_one_belong.replace({'None': None})
            df_for_one_belong = df_for_one_belong.replace({np.nan: None})

            # todo 获取目标文件路径 & 并做上下文替换
            dest_file_path = "/Users/douming/Documents/采集发布/测试文件"
            # todo 获取目标文件名 & 并做上下文替换
            dest_file_name = source_file_name + "_" + belong_value+".DBF"

            # 构造文件名
            dest_file_path_and_name = os.path.join(dest_file_path, dest_file_name)
            print(f"开始写入文件 {dest_file_path_and_name} .....")
            # 如果文件不存在，则创建空文件
            create_empty_dbf_file_if_not_exist(source_file_path_and_name, dest_file_path_and_name)
            # 写入文件,追加写入
            write_to_file(dest_file_path_and_name, df_for_one_belong)

