from engine.move_data_node.excel.move_excel_to_oracle import *
from engine.core.context import Context
from engine.cnst.FileType import FileType


def move_excel(flow_node, file_path_and_name, flow_node_excel_config, field_mapping_config_list, context_instance):
    # Move DBF file to Oracle
    move_excel_to_oracle(flow_node, file_path_and_name, flow_node_excel_config, field_mapping_config_list, context_instance)


def my_test_interface1_1703():

    """

insert into tstoretype (L_ID, C_SORUCE_TYPE, VC_TBLNAME, C_FILE_FORMATTYPE, VC_DATA_CTRL, C_DATA_TYPE, VC_CAPTION, VC_FILENAME, VC_BZ, VC_H_TBLNAME, VC_TMP_TBLNAME, VC_SOURCECOLNAME)
values (1703, '0', 'TJK_SAC_CSRCPERF', '1', '<data>
  <File SaveAs="Excel.Application"/>
  <Provider>
    Provider=Microsoft.ACE.OLEDB.12.0;Data Source="[$FILE_PATH][$FILE_NAME]";Extended Properties="Excel 12.0;HDR=NO;IMEX=1;"
  </Provider>
  <Content><![CDATA[
    select F1 as d_date, F2 as index_code,
           F3 as index_name, F4 as index_name_en,
           F5 as [open], F6 as high,
           F7 as low, F8 as [close],
           F9 as change,
           F11 as volume, F12 as turnover,
           F13 as index_market_cap, F14 as number_of_cons
      from [$A2:IU65535]
     where F1 = ''[YYYY-MM-DD]''
  ]]></Content>
  <Error ErrCode="-101" ErrStr="[csrcperf]文件未包含当天的指数行情数据，请检查文件是否匹配" Condition="@C = 0">
  select count(1) C
    from TJK_SAC_CSRCPERF a
   where a.l_ztbh=[$FUND_ID] and a.d_ywrq=to_date([YYYYMMDD],''yyyymmdd'')
</Error>
</data>', '2', '中证协--指数历史行情', 'csrcperf.xls', '', '', '', '');
    """
    file_type = FileType.EXCEL.value
    file_path_and_name = "CSRCPERF.xls"
    filter_logic = ' '
    flow_node = {
        "fieldMappingConfigList": [
            {
                "createTime": 20241204.152207,
                "fieldType": 3,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": " ",
                "processLogicType": 1,
                "sequence": 1,
                "sourceField": "F1",
                "targetField": "d_date",
                "dateFormat": "%Y-%m-%d",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 1,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "  ",
                "processLogicType": 2,
                "sequence": 2,
                "sourceField": "F2",
                "targetField": "index_code",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 1,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "  ",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "F3",
                "targetField": "index_name",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 1,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "  ",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "F4",
                "targetField": "index_name_en",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": " ",
                "processLogicType": 1,
                "sequence": 2,
                "sourceField": "F5",
                "targetField": "open",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "  ",
                "processLogicType": 2,
                "sequence": 2,
                "sourceField": "F6",
                "targetField": "high",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "   ",
                "processLogicType": 2,
                "sequence": 2,
                "sourceField": "F7",
                "targetField": "low",
                "updateTime": 20241204.152207
            },


            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "sequence": 2,
                "sourceField": "F8",
                "targetField": "close",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "dateFormat": "%Y%m%d",
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "sequence": 4,
                "sourceField": "F9",
                "targetField": "change",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "dateFormat": "%Y%m%d",
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "sequence": 4,
                "sourceField": "F11",
                "targetField": "volume",
                "updateTime": 20241204.152207
            }
            ,
            {
                "createTime": 20241204.152207,
                "dateFormat": "%Y%m%d",
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "sequence": 4,
                "sourceField": "F12",
                "targetField": "turnover",
                "updateTime": 20241204.152207
            }
            ,
            {
                "createTime": 20241204.152207,
                "dateFormat": "%Y%m%d",
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "sequence": 4,
                "sourceField": "F13",
                "targetField": "index_market_cap",
                "updateTime": 20241204.152207
            }
            ,
            {
                "createTime": 20241204.152207,
                "dateFormat": "%Y%m%d",
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "sequence": 4,
                "sourceField": "F14",
                "targetField": "number_of_cons",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "sequence": 3,
                "sourceField": "[FUND_ID]",
                "targetField": "L_ZTBH",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "dateFormat": "%Y%m%d",
                "fieldType": 3,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "sequence": 4,
                "sourceField": "[BUSINESS_DATE]",
                "targetField": "D_YWRQ",
                "updateTime": 20241204.152207
            }
        ],
        "flowNodeExcelConfig": {
          "createTime": 20241204.152206,
          "fileType": 4,
          "filterLogic": filter_logic,
          "interfaceId": "rule1_id",
          "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
          "nodeName": "node1_name",
          "nodeSeqNo": 0,
          "nodeType": 1,
          "skipRows": 1,
          "targetIntfTbl": "tjk_sac_csrcperf",
          "totalColumnCount": 14,
          "updateTime": 20241204.152206
        }
    }

    # 执行sql，获取到数据
    my_list = [
        {'S5_KEY': 102.3789, 'S6_KEY': 3.5517},
        {'S5_KEY': 0.1, 'S6_KEY': 0.2}
    ]

    context_instance = Context()
    context_instance.set('[FUND_ID]', 8888)
    context_instance.set('[BUSINESS_DATE]', 20180302)
    # 放入到上下文中
    context_instance.set('[[MY_LIST]]', my_list)

    context_instance.set('[S7]', 1)

    # 字段映射配置列表
    field_mapping_config_list = flow_node['fieldMappingConfigList']
    flow_node_excel_config = flow_node['flowNodeExcelConfig']
    move_excel(file_path_and_name, flow_node_excel_config, field_mapping_config_list, context_instance)




if __name__ == '__main__':
    my_test_interface1_1703()



