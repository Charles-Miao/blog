---
title: "Agent应用：基于TRAE的项目理解"
date: 2026-10-12T15:00:00+08:00
draft: false
toc: true
tags:
  - TRAE
  - SWDL
  - 代码理解
  - Agent
categories:
  - 技术
---

> **摘要**：本文记录了使用 TRAE Agent 深入理解联想 ProjectH SWDL（工厂量产软件下载）流程的完整过程。通过代码追踪，纠正了原有文档中的多处流程错误，发现并定位了两个生产环境偶发问题的根因，并对比了 TRAE 与 QwenPaw 在不同场景下的适用性。

---

## 背景

ProjectH SWDL 是联想笔记本工厂量产线上的软件下载部署系统，基于 WinPE + 批处理脚本驱动，涉及镜像部署、OA3 硬件哈希采集、MES 数据上报、BIOS/EC 配置及 Ship Mode 出厂装箱等工序。整套系统由数十个 .bat/.cmd 脚本组成，调用链跨越多次重启（PXE → HDD → PXE），代码量庞大且缺乏完整文档。

之前整理过一份流程文档，但其中存在一些不准确之处。本次尝试使用 TRAE Agent 对源码进行逐行追踪，验证并修正了流程描述，同时分析了两个生产偶发问题。

## TRAE 理解项目的过程

### 1. 生成 Code Wiki

首先让 TRAE 扫描整个仓库，生成结构化的 [CODE_WIKI.md](file:///c:/Users/31002026/Desktop/Desktop/LENOVO/SWDL/CODE_WIKI.md)，包含：

- 项目整体架构（分层图）
- 目录结构与模块职责（完整目录树）
- 关键脚本与函数说明（入口层 / 测试层 / OBE / 镜像部署层 / FAC / 工具）
- 依赖关系（脚本调用图 / 二进制工具 / 驱动 / 网络服务）
- 完整运行流程（三阶段）
- ProjectD 对比表

### 2. 追踪并修正流程错误

在生成 Wiki 的过程中，TRAE 通过逐行阅读代码发现了原有文档的多处错误：

#### 错误一："路线 C"不存在

原文档描述 DLSHIP.BAT 有三条路线（LFIP / OA3-FQC / 普通-OBE-非-FQC），其中"路线 C"跳过 OpenLid 直接 REHDDBOOT。

TRAE 追踪代码后发现 `:FinalCHK` 在 `CheckOS=PASS` 时直接 `goto :Check_ACState`（L315），完全跳过 `:MES_INSTALLOS`（L319）和 `:FinalCHKBIOS`（L342-378），FQC 判断代码**不可达**，实际只有两条路线。

#### 错误二：":REHDDBOOT" 不是重启

原文档写"Reboot 进入 HDD Ship Image → 在 HDD 中执行 MES/ShipMode/Shutdown"。

TRAE 逐行阅读 [DLSHIP.BAT L568-580](file:///c:/Users/31002026/Desktop/Desktop/LENOVO/SWDL/Model/Houhai14/DLSHIP/DLSHIP.BAT#L568-L580) 后发现：

```bat
:REHDDBOOT
call BIOS_load_default.bat
CALL BIOS_boot_to_HDD.BAT           ← 仅设置 BIOS 启动顺序
H2OUVE-W-CONSOLEx64.exe -uvebf disabled

:ALLPASS                             ← 直接贯穿！没有 reboot！
```

`:REHDDBOOT` 只设置 BIOS 启动顺序为 HDD，**不执行重启**，脚本直接贯穿到 `:ALLPASS`，所有收尾步骤（MES 上报、日志上传、Show SN、Ship Mode、Close MFG、电量检查、关机）都在 **WinPE** 中完成，最终 `wpeutil shutdown` 关机。

#### 错误三：完整三阶段流程

原文档将 FAC 阶段简单描述为"HDD 内执行"。

TRAE 追踪后发现完整流程是**三阶段**：

```
Phase 1 (首次 PXE): LFIP 下载镜像 → 设 HDD 启动 → 重启
Phase 2 (HDD): Windows OOBE 执行 OA30.CMD(写 OA3) + PXEBOOT.CMD(切回 PXE) → 重启
Phase 3 (二次 PXE): CheckOS=PASS → 电池→SecureBoot→DEL_OEM→REHDDBOOT(不重启)
  → MES PASS + 日志 + ShowSN + ShipMode + CloseMFG + shutdown (全程 WinPE)
```

### 3. 定位生产偶发问题

基于对代码的深入理解，分析了两个每天 600 台中 1-2 台复现的问题：

#### 问题一：黑屏（MES PASS 后、Ship Mode 前）

| 线索 | 分析 |
|------|------|
| Caps Lock 可切换 | 系统未死机，显示控制器/面板供电异常 |
| 重启后 BIOS/WinPE 都会随机黑屏 | 硬件层问题，非 OS 层 |
| 概率低（1-2/600） | 特定面板批次或 EC 固件边界条件 |

**最大嫌疑**：`H2OUVE-W-CONSOLEx64.exe -uvebf disabled`（L577），该命令写入 BIOS NVRAM 禁用 UVEBF，特定面板不兼容会导致黑屏，且设置持久化重启后仍生效。

**恢复方式**：拔 AC + 拆电池 → 长按电源键 30 秒 → EC 硬复位。

#### 问题二：电量 100%（Ship Mode 后）

代码执行顺序为：

```
1. SHIPMODE  → set_ship_mode 1        ← 进入 Ship Mode (电池隔离)
2. CloseMFG  → set_learn_mode 0       ← 退出 Learn Mode
3.            → set_test 0             ← 退出 Test Mode (可能恢复充电!)
4.            → set_mfg_mode 0         ← 退出 MFG Mode
5.            → ACStatus -c 55 75     ← 电量检查 (此时仍 55-75%)
6.            → wpeutil shutdown       ← 关机
```

**根因**：Ship Mode 在 CloseMFG 之前执行。`set_test 0` 退出 Test Mode 时可能覆盖了 Ship Mode 的电池隔离状态，如果 AC 仍连接，电池会在关机后继续充电到 100%。

**修复建议**：对调顺序，Ship Mode 放最后：

```
CloseMFG → ACStatus → SHIPMODE → shutdown
```

## TRAE vs QwenPaw 对比

在这次项目分析中，我同时使用了 TRAE 和 QwenPaw，对比两者的体验：

| 维度 | TRAE | QwenPaw |
|------|------|---------|
| **代码理解** | ★★★★★ 逐行追踪批处理脚本，交叉引用行号，发现不可达死代码 | ★★★ 可处理单文件，但跨文件调用链追踪弱 |
| **代码编写** | ★★★★★ 直接编辑项目文件，保持原有格式 | ★★★ 偏向桌面操作，代码编写非强项 |
| **问题诊断** | ★★★★★ 能结合代码逻辑 + 生产现象定位根因 | ★★★ 可分析现象，但无法深入代码验证 |
| **批量桌面任务** | ★★★ 可执行但非核心场景 | ★★★★★ 批量文件操作、桌面自动化强项 |
| **个人助理** | ★★★ 偏代码导向 | ★★★★★ 通用助理性质更浓 |
| **项目全景** | ★★★★★ 扫描整个仓库生成 Wiki，理解架构 | ★★ 缺乏项目级全局视角 |
| **交互体验** | ★★★★★ 可点击文件链接跳转源码 | ★★★ 传统对话式 |

### 总结

- **TRAE 更适合**：代码设计、代码编写、代码理解、针对代码中的问题提问和优化、跨文件调用链追踪、项目架构分析
- **QwenPaw 更适合**：批量桌面操作、文件管理、个人助理性质的任务

## 下一步计划

- 测试性修改 `H2OUVE -uvebf disabled` 行，验证黑屏是否消除
- 对调 SHIPMODE 和 CloseMFG 顺序，验证电量 100% 问题
- 用 TRAE 继续分析 ProjectD SWDL 流程，完善对比
- 探索 TRAE 的代码修改能力，尝试直接修复 DLSHIP.BAT

---

✅ 通过 TRAE 深入理解了 ProjectH SWDL 完整流程，修正了 3 处流程错误，定位了 2 个生产问题根因。TRAE 在代码理解和问题诊断方面表现出色。
