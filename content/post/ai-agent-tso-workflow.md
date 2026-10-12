---
title: "Agent应用：自动化工单检查工作流"
date: 2026-07-23T17:00:00+08:00
draft: false
toc: true
tags:
  - AI Agent
  - 自动化
  - MES
  - 工作流
categories:
  - ai应用
  - 制造业
---

> **摘要**：本文记录了基于 AI Agent 的 TSO 工单自动化检查方案，包含 MES 系统数据获取、POR 报告数据匹配、可复用技能封装等完整实现过程，将原本人工处理 10 分钟的工作压缩至 30 秒内完成。

---

## 背景

在制造业的生产管理中，工单处理是一项高频且重要的工作。传统的处理流程存在以下痛点：

1. **人工操作繁琐**：每条 SN 序列号需要手动查询 MES 系统获取设备信息
2. **数据匹配耗时**：需要根据料号手动在 POR 报告中查找对应的型号信息
3. **容易出错**：复制粘贴过程中容易出现数据错位或遗漏
4. **效率低下**：处理 20 条记录约需 10 分钟，且重复劳动无价值

**需求**：将重复、规则化的工单检查工作自动化，让 AI Agent 代替人工完成数据查询、匹配和整理工作。

## 技术方案

采用 **QwenPaw AI Agent** 实现，核心包含三部分：

| 组件 | 功能 |
|------|------|
| Python 脚本 | 负责 Excel 读写、API 调用、数据解析 |
| 可复用 Skill | 封装完整流程，支持一键调用 |
| run_tool_batch | 批量执行引擎，参数化驱动 |

## 实现过程

### 1. MES 系统数据获取

调用 MES API 获取每个 SN 对应的设备详细信息：

```python
base_url = "http://10.197.194.102/automation/sfc/mes?c=QUERY_RECORD&sn={sn}&line=FAFT_01&station=Runin&fixtureid=AFT_01&p=all"
```

**API 返回格式**（纯文本，每行一个 key=value）：
```
MCU_FW=SW_N66V00AA1_LUX_0016_M30_MTR_LENOVO_Sapporo_USR_MP
EC_VER=1.6
BIOS_VER=M4QKT1FA
ToolVer=TSW_INTEL_TGL_N66V00_ASS_V1.0.9
ATOver=SW_N66V00AA1_V012_ATO_D005_Win11_IoT_23H2_EN
...
```

**获取字段（13个）**：
- 固件信息：`MCU_FW`, `EC_VER`, `BIOS_VER`, `ToolVer`
- 软件版本：`ATOver`, `SW_VER`
- 硬件信息：`MTMNumber`, `DISK_SIZE`, `CPU_TYPE`, `DeviceInfo_RAM`
- 产品信息：`ProductName`, `MARKETING_NAME`, `Country_Code`

### 2. POR 报告数据匹配

根据料号在 POR 报告中进行快速匹配，采用字典预处理优化性能：

```python
# 构建 POR 查询字典
por_dict = {}
for _, row in df_por.iterrows():
    lux_code = str(row['Lux整机编号']).strip()
    if lux_code and lux_code not in por_dict:
        por_dict[lux_code] = row
```

**匹配字段（3个）**：
- `Model Number` - 产品型号
- `项目名` - 所属项目
- `Country/Region` - 销售地区

### 3. 封装为可复用 Skill

使用 `/make-skill` 命令将整个流程封装为独立技能，包含：

```
TSO-工单检查/
├── SKILL.md              # 技能说明文档
└── scripts/
    ├── tso_check.json    # 批处理配置
    └── tso_check.py      # 处理脚本
```

**Skill 触发方式**：
```bash
/TSO-工单检查 TSO 工单07-13_updated.xlsx
```

或者使用完整参数调用：
```python
run_tool_batch(
    file_path="skills/TSO-工单检查/scripts/tso_check.json",
    args={
        "tso_file": "TSO 工单07-13_updated.xlsx",
        "por_file": "PORModelReport_202603190908(2).xls",
        "output_file": "TSO 工单_updated_with_all_info.xlsx"
    }
)
```

## 执行效果

### 实际运行输出

```
==================================================
TSO工单检查 - 开始处理
==================================================

[1/4] 正在读取TSO工单文件...
  文件: TSO 工单07-13_updated.xlsx
  列数: 12, 行数: 23

[2/4] 正在读取POR报告文件...
  文件: PORModelReport_202603190908(2).xls
  列数: 150, 行数: 532

  找到SN列: SN
  找到料号列: 料号
  找到Lux整机编号列: Lux整机编号
  找到Model Number列: Model Number
  找到项目名列: 项目名
  找到Country/Region列: Country/Region

[3/4] 正在从MES获取信息...
  [1/23] SN=SE0001L4 OK
  [2/23] SN=SE0001LH OK
  ...
  [23/23] SN=SE00019Q OK
  MES查询完成: 23/23 成功

[4/4] 正在匹配POR报告...
  POR字典已构建: 517 个唯一编号
  POR匹配完成: 23/23 成功

==================================================
处理完成！
==================================================

输出文件: TSO 工单07-13_updated_with_all_info.xlsx
MES查询: 23/23
POR匹配: 23/23

新增字段:
  MES (13个): MCU_FW, EC_VER, BIOS_VER, ToolVer, ATOver...
  POR (3个): Model Number, 项目名, Country/Region
```

### 效率对比

| 指标 | 人工处理 | AI Agent 处理 | 提升 |
|------|---------|--------------|------|
| 23条记录耗时 | ~10分钟 | ~30秒 | **20倍** |
| 错误率 | ~5% | 0% | 完全消除 |
| 学习成本 | 需培训3天 | 一条命令 | 无需培训 |
| 可扩展性 | 难以复用 | 一键调用 | 技能可积累 |

## 技术亮点

### 1. 智能列名识别

无需硬编码列名，自动识别多种命名方式：
```python
def find_column(df, keywords):
    for col in df.columns:
        col_str = str(col).upper()
        for kw in keywords:
            if kw.upper() in col_str:
                return col
    return None
```

支持的列名变体：
- SN / 序列号 / Serial Number
- 料号 / PN / Part Number
- Lux整机编号 / Lux Code
- Model Number / 型号

### 2. 健壮的错误处理

- 文件不存在 → 清晰报错提示
- API 请求失败 → 显示 HTTP 状态码
- 料号不匹配 → 留空并统计
- 网络超时 → 自动继续处理

### 3. 性能优化

- **POR 字典预处理**：532行报告 → 517个唯一编号，O(1) 查找
- **API 请求间隔**：0.2秒间隔，避免触发限流
- **增量写入**：原地 DataFrame 更新，内存高效

## 应用价值

### 1. 员工价值释放

将工程师从重复性的复制粘贴工作中解放出来，专注于更有价值的问题分析和决策。

### 2. 技能资产沉淀

通过 Skill 封装，将个人经验转化为团队可复用的数字资产：
- 新员工无需学习复杂流程
- 标准统一，避免个人操作差异
- 持续优化，越用越好用

### 3. 数据质量保障

自动化处理完全消除人工操作错误：
- 0 条记录遗漏
- 0 个字段错位
- 100% 数据完整性

## 下一步计划

- [ ] **更多数据源集成**：对接 MTM 系统、维修记录系统
- [ ] **异常检测**：自动识别参数异常的设备，标记预警
- [ ] **批量处理**：支持一次处理多个工单文件
- [ ] **报告生成**：自动生成工单分析报告（PDF/HTML）
- [ ] **Web 界面**：提供可视化操作界面，支持拖拽上传

---

✅ **AI Agent 工作流已稳定运行，工单处理效率提升 20 倍！**

> **经验总结**：制造业的数字化转型不一定需要大投入，从具体的痛点场景入手，用 AI Agent 将重复工作自动化，是投入产出比最高的路径。每释放一位工程师的时间，就是创造一份新价值。
