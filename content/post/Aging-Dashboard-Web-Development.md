---
title: "老化看板Web程序开发"
date: 2026-08-13T21:00:00+08:00
draft: false
toc: true
tags:
  - AI Agent
  - Flask
  - Vue 3
  - SNMP
  - 工业看板
categories:
  - 技术
---

> **摘要**：本文记录了使用 AI Agent 辅助开发老化架（Run-in Rack）测试看板系统的完整过程。系统基于 Flask + MySQL + Vue 3 + Element Plus + ECharts 构建，通过 SNMP 协议采集交换机 MAC 表实现机台物理位置自动定位，部署于车间 Windows Server 内网环境。包含需求分析、架构设计、核心功能实现、部署联调及 AI 协作开发的全流程总结。

---

## 背景

工厂车间在机台老化测试环节，需要实时掌握每台机台在老化架上的测试状态和物理位置。以往依赖人工巡检和 Excel 记录，效率低且容易出错。尤其在机台数量多、老化架分层密集的场景下，"输入序列号查到机台在哪一层哪一位"本身就是一件费时费力的事。

基于这个痛点，我们决定开发一套 Web 看板系统，实现：

- 实时展示所有老化架上每个穴位（端口）的测试状态
- 通过 SNMP 协议自动采集交换机 MAC 表，实现机台物理位置自动定位
- 输入 SN 即可查到机台所在的老化架编号、层号、位号
- 按测试状态（空/进行中/超时/通过/失败）着色显示，一目了然
- 支持老化架、交换机、映射关系的可视化管理

特殊约束是：车间服务器为 Windows Server 2019 内网环境，无法访问外部 CDN，所有前端依赖必须本地化。

## 整体方案

### 架构总览

系统采用前后端分离架构，但最终由 Nginx 统一入口：

```
┌─────────────────┐     上抛(SN/MAC/IP/状态)      ┌──────────────┐
│  老化架电脑       │ ──────────────────────────► │  Flask API    │
│  upload_status.py │   POST /api/upload          │  /api/upload  │
└─────────────────┘                              └──────┬───────┘
                                                        │ 写入
                                                        ▼
┌─────────────────┐     SNMP walk (4个OID)        ┌──────────────┐
│  交换机          │ ◄────────────────────────── │  port_status  │
│  (华为/华三)     │                              │  (实时状态)    │
└─────────────────┘                              └──────┬───────┘
        ▲                                               │
        │ 每10min采集                                    │ rack_id 回填
┌───────┴─────────┐    写 switch_mac_port + 回填       │ + MAC消失清空
│ SNMP采集器        │ ──────────────────────────────────┘
│ (pysnmp版)       │
└─────────────────┘

┌─────────────────┐    GET /api/dashboard/*       ┌──────────────┐
│  浏览器前端       │ ◄────────────────────────── │  Flask API    │
│  Vue+ECharts     │    5秒轮询                    │  summary/racks│
└─────────────────┘                              └──────────────┘
```

### 技术选型

| 层 | 技术 | 选型理由 |
|---|---|---|
| 后端框架 | Flask 3.0 + flask-cors | 轻量、API 路由清晰，单文件即可管理 |
| 数据库 | MySQL 8.0 | 车间已有 MySQL 环境，数据量适中 |
| SNMP 采集 | pysnmp 4.4.12 | 纯 Python 实现，无需安装 net-snmp 工具 |
| 前端框架 | Vue 3.4 (global build) | 无需构建工具，单 HTML 文件即可 |
| UI 组件库 | Element Plus 2.6 | 表格/表单/对话框组件丰富 |
| 图表库 | ECharts 5.4 | 环形饼图效果出众，支持平滑动画 |
| WSGI 服务器 | Waitress 3.0 | Gunicorn 不支持 Windows，Waitress 是官方推荐替代 |
| 反向代理 | Nginx 1.26 | 静态文件托管 + API 反向代理 |
| 服务管理 | NSSM | 将 Flask/Nginx/SNMP 采集器注册为 Windows 服务 |

### 数据库设计

系统共 5 张核心表，数据关系如下：

```
racks (老化架)           switches (交换机)
  │  rack_no, 排数, 位数     │  switch_ip
  │  station_type            │
  │                         │
  └──────┐    ┌─────────────┘
         ▼    ▼
   rack_switch_mapping (映射关系)
     rack_id, switch_id, switch_port
         │
         │ (switch_ip + switch_port)
         ▼
   port_status (端口实时状态) ◄── switch_mac_port (MAC-端口映射)
     sn, mac, ip, test_result        switch_ip, mac_address, port_number
     start_time, timeout_seconds     (SNMP采集器每10分钟刷新)
     last_heartbeat, rack_id
```

核心设计思路：

- **`switch_mac_port`** 是 SNMP 采集的产物，存储 MAC 到物理端口的映射，是连接"机台"和"物理位置"的桥梁
- **`port_status`** 是上抛数据的归宿，每条记录代表一个机台在某端口上的测试状态
- **`rack_switch_mapping`** 定义老化架穴位与交换机端口的对应关系，新增映射时自动生成（1-2 层对应交换机1，3-4 层对应交换机2）
- 端口总数 = 排数 x 位数，运行时计算，无需单独维护字段

## 核心功能实现

### SNMP 采集：4-OID 关联链

这是整个系统最精巧的部分。要获取"MAC 地址对应交换机哪个物理端口"，看似简单，实际在华为交换机上需要经过 4 步 OID 关联：

```
MAC 十进制后缀 ──(17.4.3.1.2)──> 桥端口号
桥端口号 ──(17.1.4.1.2)──> ifIndex
ifIndex ──(31.1.1.1.1 ifName)──> 物理端口号
```

| OID | 含义 | 作用 |
|-----|------|------|
| `1.3.6.1.2.1.17.4.3.1.1` | MAC 地址表 | MAC 后缀 -> MAC 地址 |
| `1.3.6.1.2.1.17.4.3.1.2` | MAC -> 桥端口号 | MAC 后缀 -> bridge port |
| `1.3.6.1.2.1.17.1.4.1.2` | 桥端口 -> ifIndex | bridge port -> ifIndex |
| `1.3.6.1.2.1.31.1.1.1.1` | 接口名称 | ifIndex -> "GigabitEthernet0/0/2" -> port 2 |

早期版本只用 2 个 OID 直接匹配，获取的是桥端口号而非物理端口号，导致华为交换机端口映射不准。修正为 4-OID 链后，从 ifName 字段中提取真实物理端口号（如 `GigabitEthernet0/0/2` 提取 `2`）。

采集器还实现了多项关键功能：

- **多线程并行采集**：ThreadPoolExecutor 最多 8 线程，多台交换机同时采集，性能提升 8-10 倍
- **MAC 消失检测**：对比新旧 MAC 集合，消失的 MAC 对应的 port_status 自动置为 EMPTY，实现断联自动清空
- **异步 rack_id 回填**：上抛和 SNMP 采集是异步的，上抛时 MAC 表可能还没数据导致 rack_id 为 NULL。采集完成后扫描 NULL 记录，用新数据补填 switch_ip/switch_port/rack_id
- **假 up 检测**：对交换机上所有机台 IP 做并行 Ping，Ping 不通则置 EMPTY（可选功能，默认关闭以防止机台重启误清空）

### 看板仪表盘

首页看板包含 3 个 ECharts 环形饼图（TPDL/Runin/OBE 站别）和一个汇总表格。8 种状态颜色统一：

```
Empty(灰) -> Ongoing(黄) -> Fail(红) -> Pass<10min(绿) -> Timeout(蓝)
Pass 10-20min(浅紫) -> Pass 20-30min(中紫) -> Pass>30min(深紫)
```

技术上解决了两个棘手问题：

**平滑刷新**：看板每 5 秒自动刷新数据。直接重新渲染图表会导致闪烁，改用 `setOption` 增量更新 + 600ms 缓动动画，实现平滑过渡。

**v-if 切换图表消失**：Vue 的 `v-if` 会销毁重建 DOM，切回首页时 ECharts 实例绑定的 DOM 已不存在。解决方案是检测 ECharts 实例的 DOM 绑定，若不匹配则先 `dispose()` 旧实例再 `init()` 新实例。

### 机台状态生命周期

上抛仅支持 3 种状态（ONGOING/PASS/FAIL），TIMEOUT 是运行时计算得出：

```
                         上抛 ONGOING (start_time + timeout_seconds)
    EMPTY  ────────────────────────────────►  ONGOING
      ▲                                         │
      │                                         │ 当前时间 > start_time + timeout_seconds
      │                                         ▼
      │                                      TIMEOUT (仅显示，DB中仍为ONGOING)
      │                                         │
      │                                    上抛 PASS / FAIL
      │                                         ▼
      │  MAC消失 / Ping不通                    PASS / FAIL
      │ ◄───────────────────────────────────────┘
```

关键规则：

- `start_time` 仅在 ONGOING 时记录，PASS/FAIL 不覆盖
- ONGOING 超时后显示为蓝色 TIMEOUT，但运行时长不重置，继续从 start_time 累计
- PASS/FAIL 的运行时长从 `last_heartbeat`（上抛时间）累计，用于 PASS 时长分段
- 超时统计从 ongoing 中扣除，避免重复统计

### 物理位置计算

以 4 层 18 位老化架为例（position_count=18）：

| 交换机 | 端口范围 | 对应层 | 位置号 |
|--------|---------|--------|--------|
| 交换机1 | 1-18 | 第1层 | 1-18 |
| 交换机1 | 19-36 | 第2层 | 19-36 |
| 交换机2 | 1-18 | 第3层 | 37-54 |
| 交换机2 | 19-36 | 第4层 | 55-72 |

最终位置字符串格式为 `R02 第1层 第11位`。超出 36 端口范围的显示 `Unknown`。

### 位置查询闭环

输入 SN 后的完整查询链路：

```
机台 SN -> 查 port_status 得到 MAC
        -> 查 switch_mac_port 得到 switch_ip + port_number
        -> 查 rack_switch_mapping 得到 rack_id
        -> 查 racks 得到 rack_no + station_type
        -> 计算物理位置 -> "R02 第1层 第11位"
```

## AI 协作开发过程

这个项目从需求到上线，全程通过 AI Agent 协作完成。以下是分步骤的开发过程：

### 第一步：需求分析与数据库设计

向 AI 描述业务场景："车间需要看板系统，显示老化架上每台机台的测试状态和物理位置，通过交换机 MAC 表自动定位。" AI 帮助梳理出 5 张核心表的字段设计和关联关系，包括 ENUM 状态枚举、外键级联策略、索引优化建议。

这一步的关键产出是 `database.py`，包含建表逻辑和后续的自动升级迁移（字段重命名、枚举更新、索引管理）。

### 第二步：后端 API 开发

基于数据库设计，AI 逐个实现 Flask API 路由。从最核心的 `/api/upload`（上抛接口）开始，逐步扩展到看板统计、详情查询、位置查询、映射管理。

开发过程中遇到的实际问题及 AI 协作解决：

- **MAC 地址格式不统一**：不同系统上报的 MAC 格式各异（有冒号、无冒号、大小写不一），AI 建议统一归一化为 `AA:BB:CC:DD:EE:FF` 格式
- **数据库连接提前回收**：MySQL 连接对象未显式赋值给变量时出现 `Cursor is not connected` 错误，AI 定位到是连接池提前回收问题，修正为显式持有连接引用
- **统计重复 Bug**：超时状态同时被计入 ongoing 和 timeout、PASS 分段同时被计入 pass 总数，AI 帮助设计了"扣除防重复"逻辑

### 第三步：SNMP 采集器开发

这是技术难度最高的部分。最初 AI 使用 snmpwalk 命令行 + 正则解析的方案（2 个 OID），但在实际部署中发现华为交换机的端口映射不准。

AI 通过查阅华为官方文档，修正为 4-OID 关联链方案，增加了 ifIndex 转换层。同时引入 pysnmp 库替代外部命令，实现纯 Python 采集。

后续迭代的改进：

- 发现采集速度慢 -> AI 引入 ThreadPoolExecutor 并行采集
- 发现 rack_id 偶尔为 NULL -> AI 设计异步回填机制
- 发现机台拔线后状态不清空 -> AI 实现 MAC 消失检测 + Ping 假 up 检测
- pysnmp 4.4.12 与 pyasn1 版本冲突 -> AI 定位需搭配 pyasn1 < 0.5.0

### 第四步：前端看板开发

前端采用单 HTML 文件方案（Vue 3 global build），无需构建工具，适合内网部署。

AI 依次实现 4 个页面：

1. **首页看板**：3 个饼图 + 汇总表，5 秒刷新
2. **详情看板**：每个老化架的端口网格，按状态着色
3. **位置查询**：输入 SN 查物理位置
4. **维护界面**：映射/老化架/交换机的增删管理

前端遇到的问题：

- **ECharts v-if 切换消失**：AI 分析出是 Vue v-if 重建 DOM 导致 ECharts 实例失效，实现 DOM 比对 + 重新初始化逻辑
- **CDN 加载失败**：车间内网无法访问 unpkg/jsdelivr，AI 编写了 `download_libs.bat` 离线下载脚本，将所有依赖存入 `libs/` 目录
- **映射管理交互**：AI 设计了自动预览端口映射规则的前端逻辑，新增映射时实时展示生成的端口范围

### 第五步：部署与联调

部署环节 AI 提供了完整的 Windows Server 部署指南：

```bash
# 后端服务（Waitress，Windows 生产级 WSGI）
waitress-serve --host=127.0.0.1 --port=5000 --threads=8 app:app

# SNMP 采集器（独立后台进程，每10分钟一次）
python snmp_collector_pysnmp.py

# 通过 NSSM 注册为 Windows 服务（开机自启）
nssm install AgingBackend "...waitress-serve.exe"
nssm install AgingNginx "...nginx.exe"
nssm install SNMPCollector "...python.exe"
```

联调验证清单覆盖所有状态流转：

| 验证项 | 操作 | 预期结果 |
|--------|------|----------|
| 空位显示 | 新建老化架，不上抛 | 端口显示灰色 EMPTY |
| 进行中 | 上抛 ONGOING + timeout=7200 | 端口显示黄色，运行时长累计 |
| 超时 | 上抛 ONGOING + timeout=60 | 1 分钟后显示蓝色 TIMEOUT |
| 通过 | 上抛 PASS | 端口显示绿色，时长分段着色 |
| 失败 | 上抛 FAIL | 端口显示红色 |
| 断联 | 拔掉网线，等待 SNMP 采集 | 端口自动变为灰色 EMPTY |
| 位置查询 | 输入 SN 查询 | 显示老化架编号+层号+位号 |

### 第六步：问题修复迭代

上线后持续修复的问题：

- **Nginx 502**：Flask 服务未运行导致，确认 Waitress 进程存活
- **字段重命名升级**：`row_no`/`position_no` 改为 `row_count`/`position_count`，AI 编写自动迁移脚本，先检查索引存在再删除
- **查询页信息缺失**：`switch_ip` 为空时前端未显示，修复为强制显示交换机 IP、端口、老化架编号、站别
- **断联检测遗漏**：原逻辑只查 MAC 表中的记录，MAC 消失的记录无法被处理，修正为查询交换机上所有 port_status 记录

## 部署架构

最终部署在 Windows Server 2019 上，三个服务通过 NSSM 注册为系统服务，开机自启：

```
Windows Server 2019
├── Nginx (80端口)          ── 静态文件 + API反代
├── Waitress (5000端口)      ── Flask 后端
├── SNMP采集器 (后台进程)     ── 每10分钟采集
└── MySQL 8.0 (3306端口)     ── 数据存储
```

版本清单：

| 组件 | 版本 |
|------|------|
| OS | Windows Server 2019 |
| Python | 3.10.11 |
| MySQL | 8.0.37 LTS |
| Nginx | 1.26.1 |
| Waitress | 3.0.0 |
| Flask | 3.0.0 |
| Vue | 3.4.21 |
| Element Plus | 2.6.1 |
| ECharts | 5.4.3 |
| pysnmp | 4.4.12 |

## AI 协作开发总结

回顾整个开发过程，AI Agent 在以下方面发挥了关键作用：

**需求拆解**：将模糊的业务需求（"想知道机台在哪"）转化为精确的技术方案（SNMP 采集 + MAC 反查 + 物理位置计算），并主动设计数据库表结构和关联关系。

**代码生成**：从 Flask API 到 SNMP 采集器，从前端 Vue 组件到部署脚本，AI 生成了项目约 90% 的代码。开发者更多扮演"需求描述者"和"代码审查者"的角色。

**问题诊断**：上线后的问题排查效率极高。描述现象（如"图表切换页面后消失"），AI 能快速定位根因（Vue v-if 重建 DOM 导致 ECharts 实例失效）并给出修复方案。

**知识补全**：项目中涉及 SNMP 协议、华为交换机 OID 体系、Windows 服务部署等专业知识，AI 通过检索官方文档补全了这些领域知识，特别是 4-OID 关联链的修正。

**迭代优化**：从 2-OID 到 4-OID、从单线程到多线程、从心跳清理到 MAC 消失检测，每一次迭代都是基于实际运行中发现的问题，AI 提供改进方案。

## 下一步计划

- 增加管理员权限控制（登录/角色/操作日志）
- 接入告警通知（超时/失败自动推送）
- 美化看板 UI，支持大屏展示模式
- 历史数据统计与趋势分析图表
- 支持多车间多产线扩展

***
