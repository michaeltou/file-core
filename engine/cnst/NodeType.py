from enum import Enum


class NodeType(Enum):
    # 搬迁数据节点
    MOVE_DATA_NODE = 1
    # 执行sql节点
    EXECUTE_SQL_NODE = 2
    # 构建上下文节点
    BUILD_CONTEXT_NODE = 3
    # 检查文件节点
    CHECK_NODE = 4

