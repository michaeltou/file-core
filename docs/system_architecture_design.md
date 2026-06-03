# 文件网关内核（File Gateway Core）系统架构设计

> 版本：1.0 | 日期：2026-06-03

---

## 目录

- [1. 系统概述](#1-系统概述)
- [2. 架构风格与设计原则](#2-架构风格与设计原则)
- [3. 系统上下文](#3-系统上下文)
- [4. 逻辑架构](#4-逻辑架构)
- [5. 核心数据流](#5-核心数据流)
- [6. API 设计](#6-api-设计)
- [7. 组件详细设计](#7-组件详细设计)
- [8. 数据库架构](#8-数据库架构)
- [9. 并发与多进程模型](#9-并发与多进程模型)
- [10. 配置管理](#10-配置管理)
- [11. 安全考量](#11-安全考量)
- [12. 部署架构](#12-部署架构)
- [13. 已知问题与改进方向](#13-已知问题与改进方向)

---

## 1. 系统概述

### 1.1 系统定位

文件网关内核（File Gateway Core）是一个**文件解析与数据入库的中间件服务**，负责将外部来源的多种格式文件（DBF、TXT、Excel、CSV、JSON、XML、T2 API）解析为结构化数据，经过过滤、字段映射、类型转换等加工后，写入 OceanBase（Oracle 兼容模式）数据库。

### 1.2 核心能力

| 能力 | 说明 |
|------|------|
| 多格式文件解析 | 支持 7 种数据源格式，每种格式有独立的解析引擎 |
| 数据加工流水线 | 过滤 → 字段映射 → 类型转换/逻辑处理 → 入库，四阶段串行流水线 |
| 大文件多进程处理 | DBF >100 万行、TXT >100MB 自动切换多进程并行处理 |
| 数据驱动配置 | 处理规则通过请求 JSON 传入，无需修改代码即可支持新业务 |
| 上下文变量体系 | 支持标量 `[VAR]` 和集合 `[[COLLECTION.FIELD]]` 两级变量替换 |

### 1.3 系统边界

```
                     ┌─────────────┐
   外部调用方  ─────→ │ 文件网关内核 │ ─────→  OceanBase 数据库
  (资金清算系统等)    │             │
   文件系统    ─────→ │             │ ─────→  Redis (并发控制)
   T2 API     ─────→ │             │
                     └─────────────┘
```

**本系统不负责：** 文件生成、业务校验规则定义、前端界面、数据查询服务。

---

## 2. 架构风格与设计原则

### 2.1 架构风格

本系统采用**管道-过滤器（Pipe-and-Filter）** 架构风格：

```
文件读取 → [过滤器] → [字段映射器] → [逻辑处理器] → [清洗引擎] → 数据库写入
```

每个阶段独立封装，通过 pandas DataFrame 作为管道间的标准数据载体。

### 2.2 设计原则

| 原则 | 体现 |
|------|------|
| **数据驱动** | 处理规则通过 JSON 配置传入，引擎根据配置动态执行，无需为不同业务编写代码 |
| **策略模式** | 文件类型通过 `FileType` 枚举分派到独立处理器，新增格式只需增加处理器 |
| **关注点分离** | 文件读取（move_data_node）、数据加工（filter/mapping/process/clean）、数据库写入（db）各自独立 |
| **渐进式降级** | DBF 解析有 simpledbfdm → dbfreaddm 两级降级；Excel 解析有 pd.read_excel → xlsx2csv 两级降级 |

---

## 3. 系统上下文

### 3.1 外部依赖

```
┌──────────────────────────────────────────────────────────┐
│                      文件网关内核                          │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Flask    │  │ Gunicorn │  │ Waitress │  HTTP 层     │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                                          │
│  ┌────────────────────────────────────────┐              │
│  │       engine/ 业务引擎层               │              │
│  └────────────────────────────────────────┘              │
└───────┬──────────────┬──────────────┬────────────────────┘
        │              │              │
   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
   │OceanBase│   │ Redis   │   │ T2 API  │
   │(Oracle  │   │ Cluster │   │(外部HTTP│
   │兼容模式)│   │(3节点)  │   │ 服务)   │
   └─────────┘   └─────────┘   └─────────┘
        ▲
        │  读取
   ┌────┴────┐
   │文件系统  │
   │DBF/TXT/ │
   │Excel/CSV│
   │/XML     │
   └─────────┘
```

### 3.2 技术栈

| 层次 | 技术 | 版本 |
|------|------|------|
| Web 框架 | Flask | ~3.0.0 |
| WSGI 服务器 | Gunicorn (生产) / Waitress (独立) | — |
| 数据处理 | pandas + numpy | ~2.2.3 / ~1.26.3 |
| 数据库驱动 | SQLAlchemy + cx_oracle (OceanBase) | ~2.0.27 / ~2.4.1 |
| 缓存/协调 | Redis (Cluster) | ~5.2.1 |
| DBF 解析 | simpledbfdm / dbfreaddm | — |
| Excel 解析 | openpyxl / xlsx2csv | ~3.0.9 / ~0.8.4 |
| XML 解析 | lxml | ~5.1.0 |
| 限流 | ratelimit | ~2.2.1 |
| 配置 | PyYAML | ~6.0.2 |

---

## 4. 逻辑架构

### 4.1 分层架构

```
┌─────────────────────────────────────────────────────────────────┐
│  API 层                                              file_core_app.py  │
│  路由定义 · 请求解析 · 上下文初始化 · 限流 · 响应构造            │
├─────────────────────────────────────────────────────────────────┤
│  编排层                                    move_data_engine.py      │
│  流程节点分派 · 文件类型路由 · 大文件/普通文件路径选择          │
├─────────────────────────────────────────────────────────────────┤
│  文件读取层                                    move_data_node/     │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│  │ DBF  │ │ TXT  │ │Excel │ │ CSV  │ │ JSON │ │ XML  │ │  T2  │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘
├─────────────────────────────────────────────────────────────────┤
│  数据加工层                                                     │
│  ┌──────────┐ ┌──────────────┐ ┌──────────────┐ ┌───────────┐  │
│  │Filter    │→│FieldMapping  │→│ProcessEngine │→│CleanEngine│  │
│  │Engine    │ │              │ │              │ │           │  │
│  └──────────┘ └──────────────┘ └──────────────┘ └───────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  基础设施层                                                     │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐   │
│  │Context │ │  DB    │ │ Redis  │ │Config  │ │  Log       │   │
│  │上下文  │ │连接池  │ │客户端  │ │管理器  │ │日志        │   │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 核心领域对象

#### 4.2.1 Context（上下文）

Context 是贯穿整个处理流程的核心状态对象，采用**双字典同步**设计：

```
┌─────────────────────────────────────────────┐
│                  Context                     │
│                                              │
│  _context (带括号,用于变量替换):              │
│    "[FUND_ID]"      → "001"                 │
│    "[BUSINESS_DATE]" → 20241212             │
│    "[FILE_PATH]"    → "/data/file.dbf"      │
│                                              │
│  _simple_context (无括号,用于SQL绑定参数):    │
│    "FUND_ID"        → "001"                 │
│    "BUSINESS_DATE"  → 20241212              │
│    "FILE_PATH"      → "/data/file.dbf"      │
│                                              │
│  特性:                                       │
│  · 大小写不敏感 (所有key自动转大写)           │
│  · set/remove 时双字典同步更新               │
│  · 支持集合类型值 (用于 [[COLLECTION.FIELD]]) │
└─────────────────────────────────────────────┘
```

#### 4.2.2 FlowNode（流程节点）

每个请求包含一个 `flowNodeList`，定义了处理步骤序列。系统支持四类节点：

| 节点类型 | NodeType | 职责 |
|----------|----------|------|
| 数据迁移节点 | MOVE_DATA_NODE (1) | 读取文件 → 过滤 → 映射 → 入库 |
| SQL 执行节点 | EXECUTE_SQL_NODE (2) | 执行 DML SQL（带上下文参数绑定） |
| 上下文构建节点 | BUILD_CONTEXT_NODE (3) | 从 SQL/XML/常量构建上下文变量 |
| 校验节点 | CHECK_NODE (4) | 校验数据或条件，不通过则中断流程 |

#### 4.2.3 InvokeMode（调用模式）

| 模式 | 值 | 写库 | 返回数据 |
|------|---|------|---------|
| NORMAL | 1 | ✅ | ❌ |
| TEST_NO_WRITE_TO_DB | 2 | ❌ | ✅ (前10行) |
| TEST_WRITE_TO_DB | 3 | ✅ | ✅ (前10行) |

---

## 5. 核心数据流

### 5.1 主处理流程

```
HTTP POST /execute/read
│
│  ① 请求解析与上下文初始化
│
▼
┌─────────────────────────────────────────────────────────┐
│ file_core_app.py                                        │
│  · 解析 JSON 请求体                                     │
│  · 创建 Context 实例                                    │
│  · 注入标准变量: [FUND_ID], [BUSINESS_DATE], [UUID]...   │
│  · 合并 contextMap 自定义变量                            │
│  · 限流检查 (9次/秒/进程)                               │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
│  ② 遍历 flowNodeList
│
┌─── for flow_node in flow_node_list ────────────────────┐
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ move_data_engine.move_data()                    │   │
│  │  · 读取 implement_type (PAGE/SCRIPT)            │   │
│  │  · PAGE 模式: 按 FileType 分派                  │   │
│  │  · SCRIPT 模式: exec() 执行脚本                 │   │
│  └────────────────────┬────────────────────────────┘   │
│                       │                                 │
│                       ▼                                 │
│  ③ 文件读取 (以 DBF 为例)                              │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ move_dbf_to_oracle()                            │   │
│  │  · Dbf5(file_path, codec='gbk')                 │   │
│  │  · 判断是否需要多进程 (>100万行 or 接口ID=000001)│   │
│  │  · 分块读取: to_dataframe(chunk_size=10000)      │   │
│  │  · 降级: simpledbfdm → dbfreaddm                │   │
│  └────────────────────┬────────────────────────────┘   │
│                       │                                 │
│                       ▼  DataFrame                      │
│                                                         │
│  ④ 数据加工流水线 (MigrateCoreEngine.dataframe_to_oracle)│
│                                                         │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────┐ │
│  │ 4a. 过滤     │──→│ 4b. 字段映射  │──→│ 4c. 入库   │ │
│  │ FilterEngine │   │ FieldMapping │   │ to_sql()   │ │
│  │              │   │  └→ProcessEng│   │            │ │
│  └──────────────┘   └──────────────┘   └──────┬─────┘ │
│                                                │       │
│                                                ▼       │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 4d. 后置SQL执行 (CleanEngine)                    │  │
│  │  · 按 ";" 分割多条SQL                             │  │
│  │  · 替换上下文变量                                 │  │
│  │  · 逐条执行                                       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─── next flow_node ──────────────────────────────────────┘
                        │
                        ▼
│  ⑤ 构造响应
│
┌─────────────────────────────────────────────────────────┐
│ 响应构造                                                 │
│  · NORMAL: { code: 200, msg: "success" }               │
│  · TEST_*: { code: 200, data: { dataList, fieldNameList } }│
│  · 异常:   { code: -500, msg: "错误信息" }             │
│  · 限流:   { code: -429, msg: "access limit exceeded" }│
└─────────────────────────────────────────────────────────┘
```

### 5.2 大文件处理流程

```
/execute/read_big_file  或  普通接口检测到大文件
│
▼
┌─────────────────────────────────────────────────────────┐
│ 设置 Context: [READ_BIG_FILE_FLAG] = True               │
│ 不走限流检查                                            │
└───────────────────────┬─────────────────────────────────┘
                        │
          ┌─────────────┼──────────────┐
          ▼             ▼              ▼
     DBF 大文件     TXT 大文件     其他格式
          │             │           (普通路径)
          │             │
          ▼             ▼
┌─────────────────┐ ┌─────────────────────────────┐
│ 记录范围分区     │ │ 先分块读取到内存              │
│ total_records   │ │ pd.read_csv(chunksize=100000) │
│ / pool_size     │ │                               │
│ = 每进程处理量   │ │ 将 chunk 列表分配给进程池     │
└────────┬────────┘ └──────────────┬────────────────┘
         │                         │
         ▼                         ▼
┌───────────────────────────────────────────────────────┐
│ multiprocessing.Pool.starmap()                        │
│                                                       │
│  Process 0: 读取[start_0, end_0) → DataFrame → 入库   │
│  Process 1: 读取[start_1, end_1) → DataFrame → 入库   │
│  Process 2: 读取[start_2, end_2) → DataFrame → 入库   │
│  ...                                                  │
│                                                       │
│  每个进程:                                             │
│  · 独立创建 DB 引擎 (pool_size=1, 非共享)              │
│  · 独立调用 MigrateCoreEngine.dataframe_to_oracle()    │
│  · 完成后 dispose() 引擎                               │
└───────────────────────────────────────────────────────┘
         │
         ▼
┌───────────────────────────────────────────────────────┐
│ Redis 并发控制 (仅 DBF)                                │
│  SET NX key = file_path TTL = 60s                     │
│  · 防止同一 DBF 文件被并发读取（导致严重性能退化）      │
│  · 处理完毕后释放锁                                    │
└───────────────────────────────────────────────────────┘
```

---

## 6. API 设计

### 6.1 接口总览

| 接口 | 方法 | 用途 | 限流 |
|------|------|------|------|
| `/execute/read` | POST | 标准文件读取与入库 | ✅ (9次/秒/进程) |
| `/execute/read_big_file` | POST | 大文件读取与入库 | ❌ |
| `/execute/script` | POST | 执行任意 Python 脚本 | ❌ |
| `/execute/filesScript` | POST | 读取并执行磁盘上的脚本文件 | ❌ |
| `/health` | GET/POST | 健康检查 | ❌ |
| `/test` | GET/POST | 健康检查（含限流测试） | ✅ |

### 6.2 请求结构（/execute/read）

```json
{
  "filePathAndName": "/data/SJZHQ.DBF",
  "fundId": "001",
  "fundCode": "FUND001",
  "businessDate": 20241212,
  "fileId": "INTF_001",
  "fileName": "数据行情",
  "invokeMode": 1,
  "needRateLimitControl": 1,
  "encoding": "utf-8",
  "jsonData": {},
  "contextMap": {
    "CUSTOM_VAR": "custom_value"
  },
  "readRule": {
    "interfaceId": "INTF_001",
    "interfaceName": "数据行情接口",
    "flowNodeList": [
      {
        "fileFmt": "DBF",
        "rdMode": "PAGE",
        "fileFieldMappingDTOList": [...],
        "fileDbfParseRuleDTO": {...}
      }
    ]
  }
}
```

### 6.3 响应结构

```json
// 成功 (NORMAL 模式)
{ "code": 200, "msg": "success" }

// 成功 (TEST 模式)
{
  "code": 200,
  "msg": "success",
  "data": {
    "dataList": [
      { "COL_A": "value1", "COL_B": 123 }
    ],
    "fieldNameList": ["COL_A", "COL_B"]
  }
}

// 业务异常
{ "code": -500, "msg": "错误描述" }

// 校验失败
{ "code": -500, "msg": "校验不通过的具体信息" }

// 限流
{ "code": -429, "msg": "access limit is exceeded." }
```

### 6.4 两个读取接口对比

| 维度 | `/execute/read` | `/execute/read_big_file` |
|------|-----------------|--------------------------|
| 限流 | ✅ 默认启用 | ❌ 不限流 |
| `[JSON_DATA]` | ✅ 从请求提取 | ❌ 不提取 |
| DBF 处理 | 分块串行，自动升级多进程 | 直接使用多进程池 |
| CSV 处理 | ✅ | ❌ (pass) |
| DB 连接 | 共享连接池 | 每进程独立引擎 |
| 设计意图 | 通用处理 | 独立部署，少量进程共享一个进程池 |

---

## 7. 组件详细设计

### 7.1 FilterEngine（过滤引擎）

**职责：** 根据 `filterLogic` 表达式对 DataFrame 进行行级过滤。

**执行机制：** pandas `DataFrame.query()`

**变量替换（两阶段）：**

```
阶段1: 标量变量替换
  [VAR] → 从 Context 取值直接替换
  例: "FUND_ID == '[FUND_ID]'" → "FUND_ID == '001'"

阶段2: 集合变量替换（逐行展开）
  [[COLLECTION.FIELD]] → 从 Context 取集合，逐行替换后 query，结果拼接
  例: "PRODUCT_ID == '[[MY_LIST.PRODUCT]]' AND DATE == [[MY_LIST.DATE]]"
      → 遍历 MY_LIST 每一行，生成多个 query 表达式，合并结果
```

**约束：** 每个过滤表达式只允许一个集合变量。

### 7.2 FieldMapping（字段映射引擎）

**职责：** 将源字段映射到目标字段，并调用 ProcessEngine 进行类型转换和逻辑处理。

**源字段解析策略：**

```
输入: sourceField
│
├─ sourceField == "[RECNUM]"  → 生成行号列 (1, 2, 3, ...)
├─ sourceField == "[UUID]"    → 生成32位hex UUID列
├─ sourceField == "[UUID_10]" → 生成十进制UUID列
└─ 其他
   ├─ 替换 sourceField 中的 [VAR] → 得到实际列名
   ├─ 在 DataFrame 中查找该列
   │  ├─ 找到 → 使用该列数据
   │  └─ 未找到 → 从 Context 中取值作为常量列
   └─ 调用 ProcessEngine.process_process_logic()
```

**列名处理：** 源 DataFrame 列名全部转大写匹配，目标列名保持原始大小写。

### 7.3 ProcessEngine（逻辑处理引擎）

**职责：** 对字段值进行类型强制转换和业务逻辑处理。

**两阶段处理：**

```
阶段1: 类型强制转换 (fieldType)
  ┌──────────┬──────────────────────────────────────────────┐
  │ STRING   │ str() + strip() (除非 keep_original_space)  │
  │ DECIMAL  │ pd.to_numeric(errors='coerce')               │
  │ DATETIME │ pd.to_datetime(format='mixed', errors='coerce')│
  └──────────┴──────────────────────────────────────────────┘

阶段2: 业务逻辑处理 (processLogicType)
  ┌──────────┬──────────────────────────────────────────────┐
  │ SIMPLE(1)│ "$" 替换为 "x"，eval("x + 2") 逐行执行       │
  │ORIGINAL(2)│ exec() 执行任意 Python 代码，操作整个列      │
  └──────────┴──────────────────────────────────────────────┘
```

### 7.4 CleanEngine（清洗引擎）

**职责：** 执行入库前后的 SQL 语句。

```
┌──────────────────────────────────────────────────────┐
│ 入库前: process_clean_before_import()                │
│  · 读取 flow_node_config["cleanSql"]                │
│  · 替换上下文变量                                    │
│  · 执行 DELETE SQL (清除目标表已有数据)               │
│  注: 当前版本此步骤在主流程中已注释                    │
├──────────────────────────────────────────────────────┤
│ 入库后: execute_end_sql_after_import()               │
│  · 读取 flow_node_config["execSql"]                 │
│  · 按 ";" 分割为多条 SQL                             │
│  · 替换上下文变量 + 绑定参数                          │
│  · 逐条执行                                         │
└──────────────────────────────────────────────────────┘
```

### 7.5 BuildContextNode（上下文构建节点）

**职责：** 在流程节点之间动态构建上下文变量。

```
┌───────────────────────────────────────────────┐
│ BuildType.QUERY_SQL (1)                       │
│  · 执行 SQL 查询                               │
│  · SIMPLE: 单行结果，每列映射为一个上下文变量    │
│  · COLLECTION: 多行结果，整组存为集合变量       │
├───────────────────────────────────────────────┤
│ BuildType.XML_EXTRACT (2)                     │
│  · 解析 XML 文件                               │
│  · 用 XPath 提取值                             │
│  · 每个表达式结果映射为一个上下文变量           │
├───────────────────────────────────────────────┤
│ BuildType.CONSTANT_SET (3)                    │
│  · 直接 key=value 设置                         │
│  · 无 I/O 操作                                 │
└───────────────────────────────────────────────┘
```

### 7.6 CheckNode（校验节点）

**职责：** 校验数据或条件，不通过则中断流程。

```
┌───────────────────────────────────────────────┐
│ 节点校验 (check_node_engine)                   │
│  · 执行布尔表达式 (exec)                       │
│  · True = 校验不通过 (条件描述的是异常情况)     │
│  · 存储结果到 Context，返回是否继续            │
├───────────────────────────────────────────────┤
│ 数据校验 (check_file_engine)                   │
│  · checkLogicSwitch == ON 时启用               │
│  · 执行 df.query(checkLogic) 找异常行          │
│  · 存在异常行 → 抛出异常，中断流水线           │
│  · 无异常行 → 静默通过                         │
└───────────────────────────────────────────────┘
```

### 7.7 文件格式处理器

#### DBF 处理器

```
┌─────────────────────────────────────────────────────┐
│                   DBF 读取流程                       │
│                                                     │
│  Dbf5(file, codec='gbk')                            │
│       │                                             │
│       ├─ AssertionError? ──→ dbfreaddm.DBF (降级)   │
│       │                                             │
│       ├─ records > 100万 OR interface_id='000001'?   │
│       │   │                                         │
│       │   └─→ YES: 设置 [READ_BIG_FILE_FLAG]=True   │
│       │       └─→ FasterDbf5 / FasterDBFReader      │
│       │            (multiprocessing.Pool.starmap)    │
│       │            按记录范围分区并行读取+入库        │
│       │                                             │
│       └─→ NO: 分块串行读取                          │
│            to_dataframe(chunk_size=10000)            │
│            每块 → MigrateCoreEngine.dataframe_to_oracle()│
│                                                     │
│  并发控制: Redis SET NX (60s TTL)                    │
│  删除标记: 0x2A(已删除)跳过, 0x00(空)保留           │
└─────────────────────────────────────────────────────┘
```

#### TXT 处理器

```
┌─────────────────────────────────────────────────────┐
│                   TXT 读取流程                       │
│                                                     │
│  columnGetType?                                     │
│       │                                             │
│       ├─ BY_SEPARATOR                               │
│       │   │                                         │
│       │   ├─ 文件 > 100MB? → [READ_BIG_FILE_FLAG]   │
│       │   │   └─→ TextWorker 多进程处理              │
│       │   │       先分块读取到内存列表                │
│       │   │       Pool.starmap 分配到各进程           │
│       │   │                                         │
│       │   └─ 普通文件 → pd.read_csv 全量读取         │
│       │                                             │
│       ├─ BY_POSITION                                │
│       │   └─ 二进制模式读取，按字节偏移量提取列      │
│       │      无分块，全量加载                        │
│       │                                             │
│  特殊处理:                                          │
│   · mktdt04*.txt 乱码修复（二进制级拼接+清洗）       │
│   · [LINE_NO] 行号列自动插入                        │
│   · 编码降级: UTF-8 ↔ GBK 自动切换                  │
│   · 列名自动生成: F1, F2, ..., Fn (n+10列)          │
└─────────────────────────────────────────────────────┘
```

#### Excel 处理器

```
┌─────────────────────────────────────────────────────┐
│                  Excel 读取流程                      │
│                                                     │
│  configType?                                        │
│       │                                             │
│       ├─ BY_COL_POSITION                            │
│       │   └─ 列名: F1, F2, ..., Fn+10              │
│       │                                             │
│       └─ BY_COL_NAME                                │
│           └─ 按列名读取 + rename 映射                │
│                                                     │
│  读取策略 (两级降级):                               │
│   1. xlsx > 1MB → xlsx2csv 转临时CSV → pd.read_csv │
│   2. 否则 → pd.read_excel(dtype=str)               │
│   3. TypeError? → xlsx2csv 降级                     │
│                                                     │
│  所有列 dtype=str，防止数值自动转换                   │
└─────────────────────────────────────────────────────┘
```

#### 其他格式

| 格式 | 读取方式 | 特殊处理 |
|------|---------|---------|
| CSV | `pd.read_csv(chunksize)` | 编码固定 GBK；分块处理；无多进程 |
| JSON | `json.loads` + `pd.DataFrame` | 数据来自请求体 `jsonData`，非文件；支持列重命名 |
| XML | `lxml` XPath | 分块(10万条)；自动去除命名空间；支持文本/属性两种读取模式 |
| T2 | HTTP POST → JSON → DataFrame | 非文件读取；URL 可配置；列名转大写 |

---

## 8. 数据库架构

### 8.1 连接模型

```
┌─────────────────────────────────────────────────────────────────┐
│                        进程空间                                  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ OceanBaseDbUtil (单例)                                │       │
│  │  · _engine: 全局共享 SQLAlchemy Engine                │       │
│  │  · pool_size=3, max_overflow=20                      │       │
│  │  · pool_recycle=1800s, pool_timeout=30s              │       │
│  │  · URL: oracle+cx_oracle://user:pass@host:1521/db    │       │
│  │                                                      │       │
│  │  线程1 ──→ ┌─────┐                                   │       │
│  │  线程2 ──→ │连接池│ ──→ OceanBase                    │       │
│  │  线程3 ──→ └─────┘                                   │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ OceanBaseMultiProcessDbUtil (每次新建)                │       │
│  │  · get_one_process_engine(): 每次创建新 Engine       │       │
│  │  · pool_size=1, 无 max_overflow                      │       │
│  │  · 使用后 dispose()                                   │       │
│  │                                                      │       │
│  │  子进程A ──→ Engine_A (pool=1) ──→ OceanBase         │       │
│  │  子进程B ──→ Engine_B (pool=1) ──→ OceanBase         │       │
│  │  子进程C ──→ Engine_C (pool=1) ──→ OceanBase         │       │
│  └──────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

**设计原因：** SQLAlchemy Engine 的连接池在 `fork()` 后不安全，子进程必须创建独立的 Engine，不能继承父进程的连接池。

### 8.2 SQL 变量绑定机制

```
Context: [NAME] = 'Tom', [AGE] = 25
                    │
                    ▼
原始 SQL: "SELECT * FROM T WHERE name = [NAME] AND age = [AGE]"
                    │
                    ▼
SqlUtil.replace_sql():
  1. PURE_STR_REPLACE([NAME]) → 直接内联字符串值（用于 IN 子句等）
  2. 其余 [VAR] → :VAR 绑定参数语法
                    │
                    ▼
转换后: "SELECT * FROM T WHERE name = :NAME AND age = :AGE"
参数:   {'NAME': 'Tom', 'AGE': 25}
                    │
                    ▼
SQLAlchemy text(sql).bindparams(**params) → 安全执行
```

### 8.3 写入策略

```
DataFrame → to_sql(table_name, engine, if_exists='append', chunksize=动态)
│
├─ 行数 > 50000 → chunksize = 3000
├─ 行数 > 30000 → chunksize = 2000
└─ 其他         → chunksize = 1000

表名强制小写 (避免 Oracle 双引号开销)
NaN / None / 'nan' 统一替换为 Python None
```

---

## 9. 并发与多进程模型

### 9.1 HTTP 层并发

```
┌─────────────────────────────────────────────────────┐
│ Gunicorn 配置                                       │
│                                                     │
│  workers = 1 (单进程)                               │
│  threads = 10 (每进程10线程)                         │
│  worker_class = 'gthread'                           │
│                                                     │
│  ┌───────┐ ┌───────┐ ┌───────┐       ┌───────┐    │
│  │Thread1│ │Thread2│ │Thread3│  ...  │Thread10│    │
│  └───┬───┘ └───┬───┘ └───┬───┘       └───┬───┘    │
│      │         │         │                │         │
│      ▼         ▼         ▼                ▼         │
│  ┌─────────────────────────────────────────────┐   │
│  │         OceanBaseDbUtil (共享连接池)          │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 9.2 大文件多进程模型

```
┌───────────────────────────────────────────────────────────┐
│ 大文件处理进程池                                           │
│                                                           │
│  Pool(size=10, 由 read_tool.file.batch.process.pool.size) │
│                                                           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       ┌─────────┐ │
│  │Worker 0 │ │Worker 1 │ │Worker 2 │  ...  │Worker 9 │ │
│  │         │ │         │ │         │       │         │ │
│  │ Engine_0│ │ Engine_1│ │ Engine_2│       │ Engine_9│ │
│  │(pool=1) │ │(pool=1) │ │(pool=1) │       │(pool=1) │ │
│  └────┬────┘ └────┬────┘ └────┬────┘       └────┬────┘ │
│       │           │           │                  │       │
│       ▼           ▼           ▼                  ▼       │
│              OceanBase 数据库                              │
└───────────────────────────────────────────────────────────┘

数据分区策略:
  DBF: 按记录号范围 (start_index, end_index) 均分，余数分配给前几个进程
  TXT: 先分块读入内存，将 chunk 列表分配给进程池
```

### 9.3 并发控制

```
┌──────────────────────────────────────────────────────┐
│ 限流: ratelimit 库 (per-process)                      │
│  · 9 次/秒/进程                                      │
│  · needRateLimitControl=1 或缺省时启用                │
│  · needRateLimitControl=2 时跳过                      │
│  · /execute/read_big_file 不限流                      │
│                                                      │
│ 建议值: limit.calls = threads - 1                     │
│ (保证至少1个线程能返回限流响应，而非全部阻塞处理)      │
├──────────────────────────────────────────────────────┤
│ Redis 文件锁 (仅 DBF 大文件)                          │
│  · SET NX key=file_path TTL=60s                      │
│  · 防止同一 DBF 文件被并发读取                        │
│  · 处理完毕后释放                                     │
│  · 超时自动释放 (60s)                                 │
└──────────────────────────────────────────────────────┘
```

---

## 10. 配置管理

### 10.1 配置加载机制

```
MyConfig (懒加载单例)
  │
  ├─ find_application_yaml(): 从 cwd 向上逐级查找 application.yaml
  │
  ├─ get_config_value("redis.host"): 点号分隔键逐层查找
  │     application.yaml → redis → host → "172.22.4.140"
  │
  └─ 包级封装: get_config_value(key, default_value=None)
        异常或 None 时返回 default_value
```

### 10.2 关键配置项

| 配置键 | 默认值 | 用途 |
|--------|--------|------|
| `server.port` | 27777 | HTTP 服务端口 (Waitress 模式) |
| `server.threads` | 100 | Waitress 线程数 |
| `read_tool.oceanbase.*` | — | 数据库连接参数 |
| `read_tool.oceanbase.pool_size` | 3 | 连接池大小 |
| `read_tool.file.batch.process.pool.size` | 10 | 多进程池大小 |
| `dbf.chunk_size` | 10000 | DBF 分块读取大小 |
| `dbf.using_multi_process_switch_count` | 1000000 | DBF 多进程切换阈值 |
| `txt.chunk_size` | 10000 | TXT 分块读取大小 |
| `limit.calls` | 9 | 限流：每秒最大调用数 |
| `limit.period` | 1 | 限流：时间窗口(秒) |
| `redis.cluster` | true | Redis 是否集群模式 |
| `redis.nodes` | — | 集群节点列表 |
| `read_tool.t2.invoke.url` | — | T2 API 地址 |
| `read_tool.pre_warm.switch` | false | 启动预热开关 |

---

## 11. 安全考量

### 11.1 当前风险点

| 风险 | 严重程度 | 说明 |
|------|---------|------|
| **远程代码执行** | 🔴 严重 | `/execute/script` 和 `/execute/filesScript` 接口通过 `exec()` 执行用户提供的代码，无任何沙箱或权限控制 |
| **数据库凭证明文** | 🟡 中等 | `application.yaml` 中数据库密码以明文存储 |
| **SQL 注入** | 🟢 低 | SQL 参数通过 SQLAlchemy `text()` + 绑定参数执行，有效防范注入；但 `PURE_STR_REPLACE` 直接内联值仍有风险 |
| **进程逻辑执行** | 🟡 中等 | ProcessEngine 的 `SIMPLE` 模式使用 `eval()`、`ORIGINAL` 模式使用 `exec()`，可执行任意 Python 代码 |
| **文件路径遍历** | 🟡 中等 | 文件路径来自请求参数，未做路径合法性校验，可能读取服务器任意文件 |
| **Redis 无认证** | 🟡 中等 | Redis 连接未配置密码 |

### 11.2 防护措施

- SQL 执行通过参数绑定防止注入
- 限流机制防止突发流量
- Redis 文件锁防止并发资源争用
- 数据库连接池超时回收防止连接泄漏

---

## 12. 部署架构

### 12.1 标准部署

```
┌──────────────────────────────────────────────────────────┐
│ 服务器                                                    │
│                                                          │
│  ┌──────────────────────────────────────┐                │
│  │ Gunicorn Master (PID file: gunicorn.pid) │            │
│  │   Worker 1 (1进程 × 10线程)          │                │
│  └──────────────┬───────────────────────┘                │
│                 │ :27777                                 │
│                 │                                        │
│  ┌──────────────▼───────────────────────┐                │
│  │ daemon_monitor.sh (每5秒巡检)         │               │
│  │   检测 Gunicorn 进程存活              │               │
│  │   异常则自动重启                       │               │
│  └──────────────────────────────────────┘                │
│                                                          │
│  日志: ../file-core-logs/                                 │
│    gunicorn.error.log (按日轮转, 50份)                    │
│    gunicorn.access.log (按日轮转, 50份)                   │
│    app.log (按日轮转, 50份)                               │
└──────────────────────────────────────────────────────────┘
```

### 12.2 大文件独立部署（推荐）

```
┌────────────────────────┐     ┌──────────────────────────────┐
│ 普通文件服务 (端口27777) │     │ 大文件服务 (端口28888)         │
│                        │     │                              │
│ Gunicorn:              │     │ Gunicorn:                    │
│  workers=1, threads=10 │     │  workers=1, threads=少量     │
│  限流: 9次/秒           │     │  限流: 无                    │
│  进程池: 不使用          │     │  进程池: 4 workers           │
│                        │     │                              │
│ 自动升级:               │     │ 专用于大文件处理              │
│  检测到大DBF →          │     │                              │
│  HTTP → 28888          │────→│                              │
└────────────────────────┘     └──────────────────────────────┘
```

**设计意图：** 大文件服务进程少但共享一个进程池（1×4=4个处理进程），避免每个 Gunicorn Worker 各自创建进程池导致资源膨胀。

### 12.3 打包与发布

```
源码 → b.wheel.build_package.sh → dist/file_core-1.0.0-py3-none-any.whl
     → build-manual-package.sh  → dist/file_core-1.0.0-py3-none-any.whl + 部署脚本.zip
     → install_package.sh       → pip install dist/*.whl
```

---

## 13. 已知问题与改进方向

### 13.1 已知代码问题

| 问题 | 位置 | 影响 |
|------|------|------|
| `OceanBaseMultiProcessDbUtil.get_session()` 调用不存在的 `get_engine()` | `ocean_base_multi_process_db_util.py` | 多进程模式下 session 创建失败 |
| Redis 工具 `get_string()` 等方法在 `decode_responses=True` 时仍调用 `.decode('utf-8')` | `redis_util.py` | 运行时 AttributeError |
| `BelongLocalCache` 非线程安全 | `belong_local_cache_util.py` | 并发场景下缓存可能不一致 |
| `OceanBaseDbUtil` 单例初始化无线程锁 | `ocean_base_db_util.py` | 理论上可能重复创建 Engine |
| `file_process_pool.py` 全局进程池未被使用 | `file_process_pool.py` | 废弃代码 |
| `LogUtil` 包含遗留 `print()` 语句 | `LogUtil.py` | 导入时输出调试信息 |
| 入库前清洗 `process_clean_before_import()` 在主流程中被注释 | `migrate_core_engine.py` | 功能缺失 |

### 13.2 架构改进方向

| 方向 | 当前状态 | 改进建议 |
|------|---------|---------|
| **测试体系** | 无正式测试，仅有散落的集成测试脚本 | 建立单元测试 + 集成测试框架，CI/CD 流水线 |
| **代码规范** | 无 lint/format 配置 | 引入 ruff/black/isort + pre-commit |
| **安全加固** | exec() 无沙箱，凭证明文 | 脚本执行接口增加鉴权+沙箱；凭证加密或使用 Secret Manager |
| **可观测性** | 仅文件日志 | 增加 metrics (处理耗时、成功率、队列深度) 和 tracing |
| **配置管理** | 单一 YAML，无热更新 | 支持环境变量覆盖、配置热更新 |
| **大文件处理** | 多进程 + 全量加载 | 考虑流式处理框架，减少内存占用 |
| **错误恢复** | 异常直接中断 | 支持断点续传、部分失败容忍 |

---

> 文档生成时间：2026-06-03 | 基于代码库 commit: main 分支
