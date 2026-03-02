from engine.move_data_node.txt.move_txt_to_oracle import *
from engine.core.context import Context
from engine.cnst.FileType import FileType


def move_txt(flow_node, file_path_and_name, flow_node_txt_config, field_mapping_config_list, context_instance):
    # Move DBF file to Oracle
    move_txt_to_oracle(flow_node, file_path_and_name, flow_node_txt_config, field_mapping_config_list, context_instance)



def my_test_interface1_7302():

    """

insert into tstoretype (L_ID, C_SORUCE_TYPE, VC_TBLNAME, C_FILE_FORMATTYPE, VC_DATA_CTRL, C_DATA_TYPE, VC_CAPTION, VC_FILENAME, VC_BZ, VC_H_TBLNAME, VC_TMP_TBLNAME, VC_SOURCECOLNAME)
values (7302, '001', 'TJK_ZZQS_BOND_VALUATION', '2', '
<data>
<Content>
LOAD DATA
Append INTO TABLE TJK_ZZQS_BOND_VALUATION when (1:8) = ''[YYYYMMDD]''
fields terminated by ''|''
(
  s1   "trim(:s1)",
  s2   "trim(:s2)",
  s3   "trim(:s3)",
  s4   "trim(:s4)",
  s5   "trim(:s5)",
  s6   "trim(:s6)",
  s7   "trim(:s7)",
  s8   "trim(:s8)",
  s9   "trim(:s9)",
  s10  "trim(:s10)",
  s11  "trim(:s11)",
  l_ztbh constant "[$FUND_ID]",
  d_ywrq expression "to_date([YYYYMMDD],''yyyymmdd'')"
  )
</Content></data>', '2', '中证协--债券行情', '[YYYYMMDD]bond_valuation.txt', '', '', '', '');

    """
    file_type = FileType.TXT.value
    file_path_and_name = "20180302BOND_VALUATION.txt"
    filter_logic = 'F1 == [BUSINESS_DATE]'
    flow_node = {
        "fieldMappingConfigList": [
            {
                "createTime": 20241204.152207,
                "fieldType": 1,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": " ",
                "processLogicType": 1,
                "sequence": 1,
                "sourceField": "F1",
                "targetField": "S1",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 1,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "df['F2'] = df['F2'] + 'abc' ",
                "processLogicType": 2,
                "sequence": 2,
                "sourceField": "F2",
                "targetField": "S2",
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
                "targetField": "S3",
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
                "sourceField": "S4",
                "targetField": "S4",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": " $ + 1",
                "processLogicType": 1,
                "sequence": 2,
                "sourceField": "S5",
                "targetField": "S5",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "df['F6'] = df['F6'] + 1000 ",
                "processLogicType": 2,
                "sequence": 2,
                "sourceField": "F6",
                "targetField": "S6",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "df['F7'] = np.where(df['F7'] > 3, df['F7'] + 1000, df['F7']) ",
                "processLogicType": 2,
                "sequence": 2,
                "sourceField": "F7",
                "targetField": "S7",
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
        "flowNodeTxtConfig": {
          "createTime": 20241204.152206,
          "fileType": 1,
          "filterLogic": filter_logic,
          "interfaceId": "rule1_id",
          "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
          "nodeName": "node1_name",
          "nodeSeqNo": 0,
          "nodeType": 1,
          "separator": "|",
          "skipRows": 12,
          "totalColumnCount": 12,
          "targetIntfTbl": "tjk_zzqs_bond_valuation",
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
    flow_node_txt_config = flow_node['flowNodeTxtConfig']
    move_txt(file_path_and_name, flow_node_txt_config, field_mapping_config_list, context_instance)


def my_test_2_inteface_id_1025():

    #tstoretype 插入语句
    """
    insert into tstoretype (L_ID, C_SORUCE_TYPE, VC_TBLNAME, C_FILE_FORMATTYPE, VC_DATA_CTRL, C_DATA_TYPE, VC_CAPTION, VC_FILENAME, VC_BZ, VC_H_TBLNAME, VC_TMP_TBLNAME, VC_SOURCECOLNAME)
values (1025, '004', 'TJK_JYQS_SHETFQD', '2', '<data>
	<LocalParam Code="ID">select seq_public_id.nextval l_id from dual </LocalParam>
	<LocalParam Code="v_vc_etfclff">select sf_pub_getgycs([$FUND_ID],''JYQS_ETFJJTLCL'') etfclff from dual </LocalParam>
	<LocalParam Code="rq">select to_char(sf_pub_addtradedays(''1'',to_date(''[YYYYMMDD]'',''YYYYMMDD''),1,1),''YYYYMMDD'') rq from dual </LocalParam>
	<Content>
	LOAD DATA
	INFILE * "str X''0D0A''"
	Append INTO TABLE tjk_jyqs_shetfqd when (21:21) &lt;&gt; ''|'' and  vc_sz &lt;&gt; ''''
	fields terminated by ''=''
	(
	 vc_code,
	 vc_sz,
	 l_bh   constant "@ID",
	 l_lb   constant "0",
	 l_ztbh constant "[$FUND_ID]",
	 d_ywrq expression "to_date([YYYYMMDD],''yyyymmdd'')"
	)
	</Content>
	<Content>
	LOAD DATA
	INFILE * "str X''0D0A''"
	Append INTO TABLE tjk_jyqs_shetfqd when (21:21) = ''|'' and vc_name &lt;&gt; ''''
	fields terminated by ''|''
	(
	 vc_code,
	 vc_name,
	 vc_gpsl,
	 vc_tdbz,
	 vc_yjbl,
	 vc_zjbl,
	 vc_zje,
	 vc_gpsc,
	 vc_kcfx,
	 vc_by,
	 l_bh   constant "@ID",
	 l_lb   constant "1",
	 l_ztbh constant "[$FUND_ID]",
	 d_ywrq expression "to_date([YYYYMMDD],''yyyymmdd'')"
	)
	</Content>
	<Execute>
	update tjk_jyqs_shetfqd a set vc_sz= substr(a.vc_sz,1,5)||''1''
	  where a.l_ztbh=[$FUND_ID] and a.d_ywrq=to_date([YYYYMMDD],''yyyymmdd'') and a.vc_code=''Fundid1'' and a.l_lb = 0 and PKG_PUBFUN.pkgsf_pubfun_sfqy(0,''SHETFFXDDMHYQYRQ'',to_date([YYYYMMDD],''yyyymmdd'')) = 0
	</Execute>
	<Error ErrCode="-101" ErrStr="[ETF申购赎回清单]文件包含日期为[@DT]的业务数据，与当前清算日期不匹配" Condition="@C &gt; 0">
	  select count(1) C, min(trim(a.vc_sz)) DT
		from tjk_jyqs_shetfqd a
	   where a.l_ztbh=[$FUND_ID]                     and
			 a.d_ywrq=to_date([YYYYMMDD],''yyyymmdd'') and
			 a.l_lb = 0                              and
			 a.vc_code = ''TradingDay''                and
			 not ((trim(a.vc_sz) = ''[YYYYMMDD]'')  or
				  (''@v_vc_etfclff'' = ''4'' and trim(a.vc_sz) = ''@rq'' ) )
	</Error></data>', '3', '上海-ETF申购赎回清单(管理端)(交易所2.1格式)', '[$FUND_CODE][MMDD]2.ETF', null, null, null, null);
    :return:
    """

    file_type = FileType.TXT.value
    file_path_and_name = "51001009052.ETF"
    filter_logic = 'F2.notnull() '
    flow_node = {
        "fieldMappingConfigList": [
            {
                "createTime": 20241204.152207,
                "fieldType": 1,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "processLogicType": None,
                "sequence": 1,
                "sourceField": "F1",
                "targetField": "vc_code",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "F2",
                "targetField": "vc_sz",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "  ",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "[L_BH]",
                "targetField": "l_bh",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "  ",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "[L_LB]",
                "targetField": "l_lb",
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
                "targetField": "l_ztbh",
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
                "targetField": "d_ywrq",
                "updateTime": 20241204.152207
            }
        ],
        "flowNodeTxtConfig": {
          "createTime": 20241204.152206,
          "fileType": 1,
          "filterLogic": filter_logic,
          "interfaceId": "rule1_id",
          "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
          "nodeName": "node1_name",
          "nodeSeqNo": 0,
          "nodeType": 1,
          "separator": "=",
          "skipRows": None,
          "totalColumnCount": 2,
          "targetIntfTbl": "tjk_jyqs_h_shetfqd",
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
    context_instance.set('[L_BH]', 123)
    context_instance.set('[L_LB]', 0)

    # 放入到上下文中
    context_instance.set('[[MY_LIST]]', my_list)

    context_instance.set('[S7]', 1)

    # 字段映射配置列表
    field_mapping_config_list = flow_node['fieldMappingConfigList']
    flow_node_txt_config = flow_node['flowNodeTxtConfig']
    move_txt(file_path_and_name, flow_node_txt_config, field_mapping_config_list, context_instance)


def my_test_2_inteface_id_1025_part2():

    #tstoretype 插入语句
    """
    insert into tstoretype (L_ID, C_SORUCE_TYPE, VC_TBLNAME, C_FILE_FORMATTYPE, VC_DATA_CTRL, C_DATA_TYPE, VC_CAPTION, VC_FILENAME, VC_BZ, VC_H_TBLNAME, VC_TMP_TBLNAME, VC_SOURCECOLNAME)
values (1025, '004', 'TJK_JYQS_SHETFQD', '2', '<data>
	<LocalParam Code="ID">select seq_public_id.nextval l_id from dual </LocalParam>
	<LocalParam Code="v_vc_etfclff">select sf_pub_getgycs([$FUND_ID],''JYQS_ETFJJTLCL'') etfclff from dual </LocalParam>
	<LocalParam Code="rq">select to_char(sf_pub_addtradedays(''1'',to_date(''[YYYYMMDD]'',''YYYYMMDD''),1,1),''YYYYMMDD'') rq from dual </LocalParam>
	<Content>
	LOAD DATA
	INFILE * "str X''0D0A''"
	Append INTO TABLE tjk_jyqs_shetfqd when (21:21) &lt;&gt; ''|'' and  vc_sz &lt;&gt; ''''
	fields terminated by ''=''
	(
	 vc_code,
	 vc_sz,
	 l_bh   constant "@ID",
	 l_lb   constant "0",
	 l_ztbh constant "[$FUND_ID]",
	 d_ywrq expression "to_date([YYYYMMDD],''yyyymmdd'')"
	)
	</Content>
	<Content>
	LOAD DATA
	INFILE * "str X''0D0A''"
	Append INTO TABLE tjk_jyqs_shetfqd when (21:21) = ''|'' and vc_name &lt;&gt; ''''
	fields terminated by ''|''
	(
	 vc_code,
	 vc_name,
	 vc_gpsl,
	 vc_tdbz,
	 vc_yjbl,
	 vc_zjbl,
	 vc_zje,
	 vc_gpsc,
	 vc_kcfx,
	 vc_by,
	 l_bh   constant "@ID",
	 l_lb   constant "1",
	 l_ztbh constant "[$FUND_ID]",
	 d_ywrq expression "to_date([YYYYMMDD],''yyyymmdd'')"
	)
	</Content>
	<Execute>
	update tjk_jyqs_shetfqd a set vc_sz= substr(a.vc_sz,1,5)||''1''
	  where a.l_ztbh=[$FUND_ID] and a.d_ywrq=to_date([YYYYMMDD],''yyyymmdd'') and a.vc_code=''Fundid1'' and a.l_lb = 0 and PKG_PUBFUN.pkgsf_pubfun_sfqy(0,''SHETFFXDDMHYQYRQ'',to_date([YYYYMMDD],''yyyymmdd'')) = 0
	</Execute>
	<Error ErrCode="-101" ErrStr="[ETF申购赎回清单]文件包含日期为[@DT]的业务数据，与当前清算日期不匹配" Condition="@C &gt; 0">
	  select count(1) C, min(trim(a.vc_sz)) DT
		from tjk_jyqs_shetfqd a
	   where a.l_ztbh=[$FUND_ID]                     and
			 a.d_ywrq=to_date([YYYYMMDD],''yyyymmdd'') and
			 a.l_lb = 0                              and
			 a.vc_code = ''TradingDay''                and
			 not ((trim(a.vc_sz) = ''[YYYYMMDD]'')  or
				  (''@v_vc_etfclff'' = ''4'' and trim(a.vc_sz) = ''@rq'' ) )
	</Error></data>', '3', '上海-ETF申购赎回清单(管理端)(交易所2.1格式)', '[$FUND_CODE][MMDD]2.ETF', null, null, null, null);
    :return:
    """

    file_type = FileType.TXT.value
    file_path_and_name = "51001009052.ETF"
    filter_logic = 'F2.notnull() '
    flow_node = {
        "fieldMappingConfigList": [
            {
                "createTime": 20241204.152207,
                "fieldType": 1,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "processLogicType": None,
                "sequence": 1,
                "sourceField": "F1",
                "targetField": "vc_code",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 1,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "F2",
                "targetField": "vc_name",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "F3",
                "targetField": "vc_gpsl",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "F4",
                "targetField": "vc_tdbz",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "F5",
                "targetField": "vc_yjbl",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "F6",
                "targetField": "vc_zjbl",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "F7",
                "targetField": "vc_zje",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "F8",
                "targetField": "vc_gpsc",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "F9",
                "targetField": "vc_kcfx",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "F10",
                "targetField": "vc_by",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "  ",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "[L_BH]",
                "targetField": "l_bh",
                "updateTime": 20241204.152207
            },
            {
                "createTime": 20241204.152207,
                "fieldType": 2,
                "interfaceId": "rule1_id",
                "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
                "processLogic": "  ",
                "processLogicType": None,
                "sequence": 2,
                "sourceField": "[L_LB]",
                "targetField": "l_lb",
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
                "targetField": "l_ztbh",
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
                "targetField": "d_ywrq",
                "updateTime": 20241204.152207
            }
        ],
        "flowNodeTxtConfig": {
          "createTime": 20241204.152206,
          "fileType": 1,
          "filterLogic": filter_logic,
          "interfaceId": "rule1_id",
          "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
          "nodeName": "node1_name",
          "nodeSeqNo": 0,
          "nodeType": 1,
          "separator": "|",
          "skipRows": None,
          "totalColumnCount": 11,
          "targetIntfTbl": "tjk_jyqs_shetfqd",
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
    context_instance.set('[L_BH]', 123)
    context_instance.set('[L_LB]', 0)

    # 放入到上下文中
    context_instance.set('[[MY_LIST]]', my_list)

    context_instance.set('[S7]', 1)

    # 字段映射配置列表
    field_mapping_config_list = flow_node['fieldMappingConfigList']
    flow_node_txt_config = flow_node['flowNodeTxtConfig']
    move_txt(file_path_and_name, flow_node_txt_config, field_mapping_config_list, context_instance)


if __name__ == '__main__':
    my_test_interface1_7302()
    # my_test_2_inteface_id_1025()
    # my_test_2_inteface_id_1025_part2()


