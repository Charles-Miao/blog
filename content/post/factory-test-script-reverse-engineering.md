---
title: "项目理解：制造测试脚本逆向工程"
date: 2026-08-02T16:00:00+08:00
draft: false
toc: true
tags:
 - AI Agent
 - 制造测试
 - 逆向工程
 - 批处理脚本
 - 测试逻辑
categories:
 - ai应用
---

> **摘要**：本文记录了针对某笔记本工厂老化测试（RUNIN）与系统下载（SWDL）两套测试脚本体系的逆向梳理过程：从 PXE 网络启动入口出发，逐层解读 `.bat/.cmd` 脚本的调用链、测试逻辑与核心工具，最终产出完整流程文档，并沉淀出一套可复用的批处理脚本逆向方法论。

---

## 背景

工厂测试脚本（RUNIN 老化测试 / SWDL 系统下载）是笔记本产线软件环节的核心，但对维护者来说往往是个「黑盒」：

- 全部由 `.bat/.cmd` 批处理写成，无文档、无注释规范，单体系上万行
- 调用链层层嵌套：入口脚本 → 分支脚本 → 工具 EXE → MES 上报，`call`/`goto` 满天飞
- 测试逻辑藏在大段 `REM` 注释和不可达标签中，**死代码极易误导**
- 涉及 PXE/WDS 网络启动、MES BOM 比对、BIOS/EC 控制、电池充放电、SSD 健康检测等多个专业领域

目标很明确：**把脚本「翻译」成可读的流程文档，把测试逻辑画成图**，让后来者不用再啃原始代码。

## 分析过程总结

### 1. 资产盘点与脱敏

产线脚本目录共约 **15,500 个文件**，按功能分为两大体系：

| 目录 | 用途 |
|------|------|
| `Runin/` | 老化测试（跑测 + 校验） |
| `SWDL/` | 系统下载（镜像烧录 + 配置核验） |

每套体系下再按机型分支（本文用脱敏代号 **ProjectD / ProjectH** 指代）。由于脚本属于内部资产，成文前统一脱敏：机型代号替换、内部 IP / 账号密码全部用占位符代替。

### 2. 找到入口：PXE 网络启动

所有测试都从 PXE 网络启动开始，`startnet.cmd`（WinPE 启动脚本）是**总开关**：

```text
PXE 启动 → startnet.cmd → 按体系分支
  ├── RUNIN 入口：checkDL12.bat   （两机型共享）
  └── SWDL 入口：startup_X64.bat  （两机型共享，独立 WDS 服务器）
```

两条路径各自独立部署 WDS 服务器，进入后再按机型分流。

### 3. RUNIN 老化测试流程

**ProjectD —— 五阶段调用链：**

```text
Donghu-X3.BAT → WINRUNIN.BAT → Donghu-X3-RUNIN.BAT → RUNINCFG.BAT → DISM 镜像恢复
```

其中硬盘检测（CHKHDD）最有代表性，是一个**四步校验**：

1. `DiskInfoGet` 采集硬盘信息
2. `fc` 命令比对输出结果
3. SMART 阈值判断（通电次数 / 通电时间 / 不安全关机次数）
4. 不通过 → 红屏报错并上传日志

**ProjectH：**

```text
checkDL12.bat → HouHai.bat → HouHai-RUNIN.bat → RUNINDL.cmd
```

`HouHai.bat` 是入口分发脚本：装驱动 → 读 MBSN → 拉取 MES BOM → 校验机种 → 按工位判断，只有 `FCOS1` 工位才进入 RUNIN 流程。**注意**：脚本里还写有 SWDL 的路由分支，但全部是注释死代码——这是逆向时最容易踩的坑。

### 4. SWDL 系统下载流程

**ProjectD —— 可重入状态机：**

```text
donghu-x3.bat → WINSWDL.BAT → Donghu-X3-SWDL.BAT
```

`Donghu-X3-SWDL.BAT` 是基于 `AMIDEWinX64 /pat` 标志的**可重入状态机**，每执行一次推进一个阶段：

```text
预放电 → 格式化 HDD → CMOS/PXE/校时 → CFG + SecureBoot → 下载出货镜像
→ 合盖控制 → Intel ME 锁定 → HW Hash 校验 → MES 上报 → ShipMode → 关机
```

可重入设计的价值：产线断电/断网后重跑，能从上一次失败的阶段继续，而不是从头再来。

**ProjectH —— 准备 + 主线烧录：**

```text
startup_X64.bat → Houhai14TEST.cmd → DLSHIP.BAT
```

`startup_X64.bat` 自行完成 14 步准备（机型读取 / 工具复制 / MES BOM / 工位判断 / 电池控制 / SecureBoot 禁用等），然后直接调 `Houhai14TEST.cmd` → `DLSHIP.BAT` 走主线烧录：

```text
OA3 拷贝 → AC 检测 → TCM 启用 → LFIP 镜像 → BIOS 校验 → 电池 50-80%
→ SecureBoot → BCD 重置 → OEM 删除 → LID 测试 → MES 上报 → PASS → ShipMode → 关机
```

另一个工位（OBE）则完全不同：直接执行 `SWDL2_OBE.bat`，这是一个 **17 步的硬件配置核验脚本**，只做检查不做烧录（脚本后半段完整的 MOPS 烧录逻辑全是死代码，`CHKBIOS-ECVer` 一通过就 `goto PXEBoot` 退出）。

### 5. 测试逻辑的共性套路

梳理完全部脚本后，发现工厂测试逻辑高度模板化，基本是这几板斧：

1. **MES BOM 比对**：`wmic` 读本机 SN/UUID/CPU/RAM/SSD，与 MES 下发的 BOM 逐项比对，不符 → 红屏循环
2. **硬件设备核验**：`devcon` 查 USB/PCI/显示器设备 ID，匹配 BOM 白名单（蓝牙、摄像头、显卡、屏幕、无线网卡）
3. **SSD 健康度检查**：`smartctl -A` 看 Critical Warning、通电次数 <1000、通电时间 <200h、不安全关机 <300、Media Errors = 0
4. **电池控制**：EC 工具设置电池学习模式（60-70% 区间）、合盖测试模式，确保测试过程屏幕不灭
5. **BIOS/EC 版本校验**：当前版本与 MES BOM 比对，不匹配不进下一阶段
6. **日志上报**：所有结果按 SN 分目录 copy 到网络盘，失败也照常上报（FAIL 目录）

### 6. 逆向方法论总结

- **从 PXE 入口顺藤摸瓜**：`startnet.cmd` 是总开关，先找到它
- **先去注释再读流程**：把 `REM` 块和不可达标签标出来，避免被死代码带偏
- **grep 调用关系**：`grep -rn "call .*\.bat"` 一网打尽所有调用点
- **识别状态机**：靠标志文件 / 参数（如 `/pat`）分段推进的脚本，按阶段画状态图
- **可视化输出**：调用链画成图（Mermaid/流程图），比读代码快 10 倍
- **交叉验证**：以 MES 工位名（站别）为线索，反向确认各分支脚本的真实归属

## 下一步计划

- 补齐 ProjectH RUNIN 内部各子脚本的详细注释
- 梳理 BIOS/EC 版本升级与 MES 配置项的对应关系
- 整理一份「产线脚本常见套路速查表」
- 尝试把状态机脚本用 Python 重写并做模拟验证

---

✅ 逆向梳理完成，全部流程文档已同步到 GitHub 仓库，后续持续更新！
