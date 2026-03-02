
from engine.db.oracle_read_tool_db_util import *
from engine.process.process_engine import ProcessEngine
from engine.filter.filter_engine import FilterEngine

class FieldMapping:
    def __init__(self):
        pass

    # 处理字段映射
    @staticmethod
    def process_field_mapping(df, field_mapping_config_list, context_instance):
        result_df = pd.DataFrame()
        df.columns = df.columns.str.upper()
        column_names_in_files = df.columns
        for field_mapping_item in field_mapping_config_list:
            source_field = field_mapping_item['sourceField'].upper().strip()
            # 这里target_field 目标字段，不能统一转成大写，因为有可能数据库字段就是小写的，所以配置什么，这里就用什么，不做默认的统一转换
            target_field = field_mapping_item['targetField']
            process_logic = field_mapping_item.get('processLogic')
            process_logic_type = field_mapping_item.get('processLogicType')
            field_type = field_mapping_item.get('fieldType')
            date_format = field_mapping_item.get('dateFormat')

            # 对dataFrame中的行号RECNUM，进行处理，这样在映射配置中，就可以使用RECNUM作为源字段
            if source_field == '[RECNUM]':
                df['[RECNUM]'] = df.reset_index().index + 1
                # result_df[target_field] = df['[RECNUM]']
                #  1 按照配置的加工逻辑处理处理源dataframe数据
                ProcessEngine.process_process_logic(df, source_field, process_logic, process_logic_type, field_type,
                                                    date_format)
                #  2 将处理后的数据，赋值给目标dataFrame
                result_df[target_field] = df[source_field]

            else:  # 非'RECNUM'字段的处理
                # 保留原始值
                original_source_field = source_field
                # 把source_field中的变量替换成上下文的变量.例如： source_field =F[JE] 转成 source_field =F2
                used_param_list_in_source_field = FilterEngine.get_used_simple_param_list(source_field)
                if used_param_list_in_source_field:
                    for param_item in used_param_list_in_source_field:
                        context_param_key = '[' + param_item + ']'
                        # 如果原始来源字符串original_source_field字符串和从匹配出来的值加上[]后是相等的，则不需要做“上下文变量替换”。
                        # 举例：比如[FUND_ID],就不需要替换。F[COLUMN_NUMBR] 就需要替换成F2。
                        if original_source_field == context_param_key:
                            pass
                        else:
                            context_param_value = context_instance.get(context_param_key)
                            source_field = source_field.replace(context_param_key, str(context_param_value))

                if process_logic:
                    # 把process_logic中的变量替换成上下文的变量. 例如 df['F[JE]'] = df['F[JE]'] + 1 转成 df['F2'] = df['F2'] + 1
                    used_param_list_in_process_logic = FilterEngine.get_used_simple_param_list(process_logic)
                    if used_param_list_in_process_logic:
                        for param_item in used_param_list_in_process_logic:
                            context_param_key = '[' + param_item + ']'
                            context_param_value = context_instance.get(context_param_key)
                            process_logic = process_logic.replace(context_param_key, str(context_param_value))


                # 如果配置的源字段在源文件中存在，则按照下面的方式处理
                if source_field in column_names_in_files:
                    #  1 按照配置的加工逻辑处理处理源dataframe数据
                    ProcessEngine.process_process_logic(df, source_field, process_logic, process_logic_type, field_type, date_format)
                    #  2 将处理后的数据，赋值给目标dataFrame
                    result_df[target_field] = df[source_field]

                #
                elif source_field in context_instance:
                    #
                    context_value = context_instance.get(source_field)
                    #
                    df[source_field] = context_value
                    # 1 按照配置的加工逻辑处理处理源dataframe数据
                    ProcessEngine.process_process_logic(df, source_field, process_logic, process_logic_type, field_type, date_format)
                    # 2 将处理后的数据，赋值给目标dataFrame
                    result_df[target_field] = df[source_field]

        return result_df
