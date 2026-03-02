from engine.cnst.BuildType import BuildType
from engine.build_context_node.build_context_from_xml import build_context_from_xml
from engine.build_context_node.build_context_from_sql import build_context_from_sql
from engine.build_context_node.build_context_from_constant import build_context_from_constant


def build_context(flow_node, context_instance):
    """
    根据 flow_node 的配置，构造上下文
    :param flow_node:
    :param context_instance:
    :return:
    """
    flow_node_build_context_config = flow_node['flowNodeBContextConfig']
    if flow_node_build_context_config is None:
        return

    build_type = flow_node_build_context_config['buildType']
    if build_type == BuildType.QUERY_SQL.value:
        # sql 构造上下文
        build_context_from_sql(flow_node, context_instance)
    elif build_type == BuildType.XML_EXTRACT.value:
        # xml 构造上下文
        build_context_from_xml(flow_node, context_instance)
    elif build_type == BuildType.CONSTANT_SET.value:
        build_context_from_constant(flow_node, context_instance)
    else:
        raise Exception('Invalid build type for context node.')




