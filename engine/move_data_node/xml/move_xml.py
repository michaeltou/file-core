from engine.move_data_node.xml.move_xml_to_oracle import *
from engine.core.context import Context
from engine.cnst.FileType import FileType
from engine.cnst.NodeType import NodeType
from engine.cnst.FieldType import FieldType
from engine.move_data_node.xml.move_xml_to_oracle_with_xpath import *


def move_xml(flow_node, file_path_and_name, flow_node_xml_config, field_mapping_config_list, context_instance):
    # Move DBF file to Oracle
    move_xml_to_oracle_with_xpath(flow_node, file_path_and_name, flow_node_xml_config, field_mapping_config_list, context_instance)



def my_test_interface1_1107():

    """

insert into tstoretype (L_ID, C_SORUCE_TYPE, VC_TBLNAME, C_FILE_FORMATTYPE, VC_DATA_CTRL, C_DATA_TYPE, VC_CAPTION, VC_FILENAME, VC_BZ, VC_H_TBLNAME, VC_TMP_TBLNAME, VC_SOURCECOLNAME)
values (1107, '004', 'TJK_JYQS_SZETFQD_XML', '4',
 '<Proc DataPath="" Desc="深圳--ETF申购赎回清单">
<Param Code="A" ValuePath="CreationRedemptionUnit/text()"/>
<Param Code="B" ValuePath="EstimateCashComponent/text()"/>
<Param Code="C" ValuePath="CashComponent/text()"/>
<Param Code="D" ValuePath="SecurityID/text()"/>
<Param Code="E" ValuePath="Creation/text()"/>
<Param Code="F" ValuePath="Redemption/text()"/>
<Param Code="G" ValuePath="TradingDay/text()"/>
<Param Code="H" ValuePath="PreTradingDay/text()"/>
<Param Code="I" ValuePath="DividendPerCU/text()"/>
<Param Code="J" ValuePath="NAV/text()"/>
<Param Code="K" ValuePath="NAVperCU/text()"/>
<Param Code="L" ValuePath="TotalRecordNum/text()"/>
<Param Code="M" ValuePath="MaxCashRatio/text()"/>
<Param Code="N" ValuePath="Publish/text()"/>
<Param Code="X" ValuePath="Symbol/text()"/>
<Param Code="Y" ValuePath="FundManagementCompany/text()"/>
<Param Code="Z" ValuePath="UnderlyingSecurityID/text()"/>
<Param Code="O" ValuePath="Components/Component[#Index]/UnderlyingSecurityID/text()"/>
<Param Code="P" ValuePath="Components/Component[#Index]/UnderlyingSecurityIDSource/text()"/>
<Param Code="Q" ValuePath="Components/Component[#Index]/UnderlyingSymbol/text()"/>
<Param Code="R" ValuePath="Components/Component[#Index]/ComponentShare/text()"/>
<Param Code="S" ValuePath="Components/Component[#Index]/SubstituteFlag/text()"/>
<Param Code="T" ValuePath="Components/Component[#Index]/PremiumRatio/text()"/>
<Param Code="U" ValuePath="Components/Component[#Index]/DiscountRatio/text()"/>
<Param Code="V" ValuePath="Components/Component[#Index]/CreationCashSubstitute/text()"/>
<Param Code="W" ValuePath="Components/Component[#Index]/RedemptionCashSubstitute/text()"/>
<Param Code="AA" ValuePath="Components/Component[#Index]/MappingSecurityID/text()"/>
<Param Code="AB" ValuePath="Components/Component[#Index]/PhysicalCreationRedemption/text()"/>
<Content Type="Query">select seq_public_id.nextval LD,''to_date([YYYYMMDD],''''yyyymmdd'''')'' DA from dual
<Param Code="ld" ValuePath="METADATA/ROWDATA/ROW/@LD"/>
<Param Code="da" ValuePath="METADATA/ROWDATA/ROW/@DA"/></Content>
<Content Type="Execute">
insert into TJK_JYQS_SZETFQD_XML(l_ztbh,d_ywrq,vc_code , vc_sz,l_glbh,L_BH,L_LB,L_HH)
select [$FUND_ID],@da,''CreationRedemptionUnit'',''@A'',@ld,@ld,0,2 from  dual union all
select [$FUND_ID],@da,''EstimateCashComponent'',''@B'',@ld,@ld,0,3 from  dual union all
select [$FUND_ID],@da,''CashComponent'',''@C'',@ld,@ld,0,4 from  dual union all
select [$FUND_ID],@da,''FundID'',''@D'',@ld,@ld,0,5 from  dual union all
select [$FUND_ID],@da,''Creation'',''@E'',@ld,@ld,0,6 from  dual union all
select [$FUND_ID],@da,''Redemption'',''@F'',@ld,@ld,0,7 from  dual union all
select [$FUND_ID],@da,''TradingDay'',''@G'',@ld,@ld,0,8 from  dual union all
select [$FUND_ID],@da,''PreTradingDay'',''@H'',@ld,@ld,0,9 from  dual union all
select [$FUND_ID],@da,''DividendPerCU'',''@I'',@ld,@ld,0,10 from  dual union all
select [$FUND_ID],@da,''NAV'',''@J'',@ld,@ld,0,11 from  dual union all
select [$FUND_ID],@da,''NAVperCU'',''@K'',@ld,@ld,0,12 from  dual union all
select [$FUND_ID],@da,''TotalRecordNum'',''@L'',@ld,@ld,0,13 from  dual union all
select [$FUND_ID],@da,''MaxCashRatio'',''@M'',@ld,@ld,0,14 from  dual union all
select [$FUND_ID],@da,''Publish'',''@N'',@ld,@ld,0,15 from  dual l union all
select [$FUND_ID],@da,''FundName'',''@X'',@ld,@ld,0,16 from  dual union all
select [$FUND_ID],@da,''FundManagementCompany'',''@Y'',@ld,@ld,0,17 from  dual union all
select [$FUND_ID],@da,''UnderlyingIndex'',''@Z'',@ld,@ld,0,18 from  dual
</Content>
<Content Type="Execute" LoopPath="Components/Component">insert into TJK_JYQS_SZETFQD_XML(l_ztbh,d_ywrq,l_hh,vc_scbz,vc_code,vc_name, vc_gpsl,vc_tdbz,vc_yjbl,vc_zjbl,vc_zje,vc_shzje,vc_gpsc,l_bh,l_glbh,l_lb,vc_ysdm,vc_sfswdjss)
values ([$FUND_ID],@da,20+#Index,''@P'',''@O'',:Q,''@R'',''@S'',''@T'',''@U'',
''@V'',''@W'',''@P'',@ld,@ld,1,''@AA'',''@AB'')</Content></Proc>', '2', '深圳--ETF申购赎回清单(XML文件)', 'pcf_[$FUND_CODE]_[YYYYMMDD].xml', null, null, null, null);

    """
    file_type = FileType.XML.value
    file_path_and_name = "pcf.intf_id1107.xml"
    filter_logic = '  '
    flow_node = {
        "fieldMappingConfigList": [
            {
                "fieldType": FieldType.DECIMAL.value,
                "processLogic": "$+20",
                "sourceField": "INDEX",
                "targetField": "l_hh",
            },
            {
                "fieldType": FieldType.STRING.value,
                "sourceField": "UnderlyingSecurityIDSource",
                "targetField": "vc_scbz",
            },
            {
                "fieldType": FieldType.STRING.value,
                "sourceField": "UnderlyingSecurityID",
                "targetField": "vc_code",
            },

            {
                "fieldType": FieldType.STRING.value,
                "sourceField": "UnderlyingSymbol",
                "targetField": "vc_name",
            },
            {
                "fieldType": FieldType.STRING.value,
                "sourceField": "ComponentShare",
                "targetField": "vc_gpsl",
            },
            {
                "fieldType": FieldType.STRING.value,
                "sourceField": "SubstituteFlag",
                "targetField": "vc_tdbz",
            },

            {
                "fieldType": FieldType.STRING.value,
                "sequence": 1,
                "sourceField": "PremiumRatio",
                "targetField": "vc_yjbl",
            },
            {
                "fieldType": FieldType.STRING.value,
                "sourceField": "DiscountRatio",
                "targetField": "vc_zjbl",

            },

            {
                "fieldType": FieldType.STRING.value,
                "sourceField": "CreationCashSubstitute",
                "targetField": "vc_zje",
            },


            {
                "fieldType": FieldType.STRING.value,
                "sourceField": "RedemptionCashSubstitute",
                "targetField": "vc_shzje",
            },
            {
                "fieldType": FieldType.STRING.value,
                "sourceField": "UnderlyingSecurityIDSource",
                "targetField": "vc_gpsc",
            },
            {
                "fieldType": FieldType.DECIMAL.value,
                "sourceField": "[SEQUENCE]",
                "targetField": "l_bh",
            },
            {
                "fieldType": FieldType.DECIMAL.value,
                "sourceField": "[SEQUENCE]",
                "targetField": "l_glbh",
            },
            {
                "fieldType": FieldType.DECIMAL.value,
                "sourceField": "[CONSTANT_1]",
                "targetField": "l_lb",
            },
            {
                "fieldType": FieldType.STRING.value,
                "sourceField": "MappingSecurityID",
                "targetField": "vc_ysdm",
            },
            {
                "fieldType": FieldType.STRING.value,
                "sourceField": "PhysicalCreationRedemption",
                "targetField": "vc_sfswdjss",
            },
            {
                "fieldType": FieldType.DECIMAL.value,
                "sourceField": "[FUND_ID]",
                "targetField": "L_ZTBH",
            },
            {
                "dateFormat": "%Y%m%d",
                "fieldType": FieldType.DATETIME.value,
                "sourceField": "[BUSINESS_DATE]",
                "targetField": "D_YWRQ",
            }
        ],
        "flowNodeXmlConfig": {

          "fileType": 1,
          "filterLogic": filter_logic,
          "interfaceId": "rule1_id",
          "nodeId": "62879a48-1ea8-4fc3-b73a-1ab01cfbd21f",
          "nodeName": "node1_name",
          "nodeSeqNo": 0,
          "nodeType": NodeType.MOVE_DATA_NODE.value,
          "valuePath": "Components",

          "targetIntfTbl": "tjk_jyqs_szetfqd_xml",

        }
    }

    context_instance = Context()
    context_instance.set('[FUND_ID]', 8888)
    context_instance.set('[BUSINESS_DATE]', 20180302)
    context_instance.set('[SEQUENCE]', 10001)
    context_instance.set('[CONSTANT_1]', 1)


    # 字段映射配置列表
    field_mapping_config_list = flow_node['fieldMappingConfigList']
    flow_node_xml_config = flow_node['flowNodeXmlConfig']
    move_xml(file_path_and_name, flow_node_xml_config, field_mapping_config_list, context_instance)




if __name__ == '__main__':
    my_test_interface1_1107()


