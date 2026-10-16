---
title: "Wallaby DL OS NG 失效分析"
date: 2022-05-17T12:00:00+08:00
draft: false
toc: true
tags:
  - 失效分析
  - Wallaby
  - DL
  - MCP
  - Bad Block
categories:
  - FA报告
---

> **摘要**：本文记录了Wallaby机型TV阶段Shipping Image下载失败（DL OS NG）问题的完整失效分析过程，涵盖问题描述、人机料法环全方位排查、根本原因定位以及短期/长期改善措施。

---

## 问题描述

- **机型**：Wallaby
- **发生时间**：2022年02月14日
- **发生阶段**：TV（共5机）
- **不良率**：0.5%~1.0%（年前约0.2%）
- **现象描述**：Wallaby Shipping image 下载失败，设备管理器中无法识别到设备；
  NG主板回流PCBA后，100%可以强制下载test image。

---

## 问题分析（人机料法环）

### 历史数据分析

通过Wallaby DL NG历史数据分析：

1. **时间趋势**：问题初始发生于2月份，断断续续出现高不良，集中爆发时间为3月至5月初。
2. **不良率走势**：
   - 2月初：F/R约 0.2%
   - 2月下半月：F/R升至约 0.7%
   - 3月：F/R约 0.9%
   - 4~5月初：F/R约 1.1%
3. **失败阶段**：DL NG机台绝大多数在烧录 **System file** 和少量烧录 **Modem file** 时fail，错误类型为 `status read failed (too many links)`。
4. **治具分布**：捞取NG机台UI log发现，NG未集中出现在某个治具，排除治具单点问题。

### 人（人员作业手法）

排查动作：
- 测试人员盯站确认作业手法
- 治具清洁

**结论**：以上动作均无改善，**排除人员因素**。

### 机（设备/治具）

排查动作：
- 两套cradle治具更换为顶针治具
- 3/15使用台北寄出新底座
- 更换I5 8G高配电脑
- 清理电脑中USB HWID、device ID等注册表信息

**结论**：以上动作均无改善，**排除治具和测试电脑因素**。

### 料（物料/MCP）

排查动作：
- NG机台MCP送厂商分析，结果为 **NTF**（No Trouble Found）
- 将NG机台的MCP植球到OK板子上进行DL shipping loopback测试，**不良现象跟随MCP**
- OK机台来回DL shipping和factory共300次，未发生fail现象
- 5/8抓取NG MB DL fail的UART log，log显示烧录system file时出现 **bad block**，随后烧录中断，机台USB连接断开，且无法再识别到装置
- 确认4月底至5月初MCP D/C：
  - SMT P13616400E-2148
  - SMT P14208300E-2202（提供UART log的板子为此code）
  - SMT P14025400E-2202

**结论**：不良现象跟随MCP，且UART log确认出现bad block，**料件（MCP）为主要怀疑方向**。

### 法（测试方法/流程）

排查动作：
- RD初次建议将modem和system烧录顺序往前调整，验证后未能起效
- Qualcomm建议flash modem和system file前先做 **erase** 这两个分区的动作
- 5/12~5/14 try run验证，**无烧录modem & system fail的issue**

**结论**：烧录前增加erase分区动作可有效解决此问题。

### 环（环境因素）

排查动作：
- RD考虑错误信息显示"too many links"，可能是电脑USB接口供给cradle的5V不稳定导致
- 建议增加USB HUB转接（HUB有额外电源供电）
- 验证测试3号、4号测试电脑HUB转接，**并无改善**

**结论**：以上动作均无改善，**排除环境因素**。

### 分析总结

> 初步分析 **MCP bad block问题** 导致Wallaby TV DL高不良。

---

## 根本原因

**Root Cause**：初步分析 **MCP bad block数量超标或bad block集中在key partition**，导致烧录指令无法完成烧录动作。而system file属于系统关键文件，此部分烧录fail导致机台USB断开，无法识别装置。

关于MCP厂商对于Bad block管控的规格：
> bad blocks 的规格为 original bad block > 40 为不良品

近期MCP bad block数量和分布状况，待TM与厂商确认是否可以提供。

---

## Action

### Short Term（短期对策）

1. 在flash modem和system分区文件前，先做 **erase分区** 动作（5/16开会正式导入）
2. PD和FAE区分fail状况，根据fail状况再加入其他的erase指令

### Long Term（长期对策）

1. 收集NG MCP D/C信息提供给TM，待TM与MCP厂商确认关于bad block是否有改善的机会
2. 将 **Erase动作作为标配** 加入image download流程中

---

✅ 失效分析完成，短期对策已验证有效，长期对策持续跟进中！
