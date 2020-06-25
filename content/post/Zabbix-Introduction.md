---
title: "Zabbix Introduction"
date: 2019-11-14T18:26:47+08:00
description: ""
draft: false
tags: [Zabbix]
categories: [运维]
---

## Zabbix介紹

Alexei Vladishev 创建了Zabbix 项目, 当前处于活跃开发状态, Zabbix SIA提供支持.

- Zabbix 是一个**企业级的**、**开源的**、分布式的监控套件
- Zabbix **可以监控网络和服务的状况**. Zabbix 利用灵活的告警机制，允许用户对事件发送基于Email 的告警.这样可以保证快速的对问题作出相应. Zabbix 可以利用存储数据提供杰出的报告及图形化方式. 这一特性将幫助用户完成容量规划.
- Zabbix 支持polling 和trapping 两种方式. **所有的Zabbix 报告都可以通过配置参数在WEB 前端进行访问**. Web前端将帮助你在任何区域都能够迅速获得你的网络及服务状况. Zabbix 可以通过尽可能的配置来扮演监控你的IT 基础框架的角色，而不管你是来自于小型组织还是大规模的公司.
- Zabbix 是**零成本**的. 因为Zabbix 编写和发布基于GPL V2 协议. 意味着源代码是免费发布的.
- Zabbix 公司也提供**商业化的技术支持**.

## Zabbix特性

- 数据收集（系統可用性/SNMP/IPMI/自定義）
- 灵活的阀值定义（觸發器Trigger）
- 高级告警配置
- 实时绘图
- 扩展的图形化显示（聚合圖/網絡拓撲圖）
- 历史数据存储（趨勢數據）
- 配置简单（可以使用模板）
- 模板使用（可繼承）
- 网络自动发现（網絡設備/文件系統/網卡設備/SNMP OID等）
- 快速的web 接口
- Zabbix API（二次開發）
- 权限系统
- 全特性、agent 易扩展（支持Windows和Linux）
- 二进制守护进程（C 开发，高性能，低内存消耗，易移植）
- 具备应对复杂环境情况

## Zabbix安裝和手冊

- 服務端配置

[https://my.oschina.net/zhangyangyang/blog/841043](https://my.oschina.net/zhangyangyang/blog/841043)

- Windows客戶端配置

[https://www.jianshu.com/p/9befd0bc7188](https://www.jianshu.com/p/9befd0bc7188)

- 官方手冊

[https://www.zabbix.com/documentation/3.4/zh/manual](https://www.zabbix.com/documentation/3.4/zh/manual)

- 非官方手冊

《Zabbix 教程从入门到精通》

作者：凉白开

电子书：[http://ebook.ttlsa.com/monitor/](http://ebook.ttlsa.com/monitor/)

文章列表：[http://www.ttlsa.com/zabbix/follow-ttlsa-to-study-zabbix/](http://www.ttlsa.com/zabbix/follow-ttlsa-to-study-zabbix/)

## Zabbix應用（數據采集）

- Agentd客戶端自帶item key（CPU/内存使用率等）

![own](https://raw.githubusercontent.com/Charles-Miao/blog/master/static/Zabbix-Introduction/1.png)

- Agentd客戶端自定義item key/ 自定義檢查脚本（DELL服務器硬件運行狀況：溫度/風扇/内存/網卡/CPU/硬盤/邏輯磁盤/Power Supply等）

![custom](https://raw.githubusercontent.com/Charles-Miao/blog/master/static/Zabbix-Introduction/2.png)

- 自定義item key和檢查脚本透過sender指令發送給服務器，同時服務器配置Trapper監控項（CPU型號/CPU數量/OS版本等），主要用於Zabbix獲取數據有超時的情況

![sender](https://raw.githubusercontent.com/Charles-Miao/blog/master/static/Zabbix-Introduction/3.png)

- HP服務器硬件監控（溫度/風扇/内存/網卡/CPU/硬盤/Power Supply等）

帶外：iLO網口設定/IPMI設定/SNMP設定/SNMP OID

帶内：系統内SNMP設定/HP ProLiant Insight Management Agents/ SNMP OID

![snmp_ipmi](https://raw.githubusercontent.com/Charles-Miao/blog/master/static/Zabbix-Introduction/4.png)

## Zabbix應用（圖形展示）

- 圖形

![graph](https://raw.githubusercontent.com/Charles-Miao/blog/master/static/Zabbix-Introduction/5.png)

- 聚合圖形
- 拓撲圖

![topology](https://raw.githubusercontent.com/Charles-Miao/blog/master/static/Zabbix-Introduction/6.png)

## Zabbix應用（觸發通知）

- 觸發（CPU使用率高於60%/ 内存空間小於2G/ 磁盤空間小於20%/ 服務器5分鐘連接不到/ 風扇故障/ CPU故障燈硬件異常等）
- CPU使用率異常觸發報警

![trigger](https://raw.githubusercontent.com/Charles-Miao/blog/master/static/Zabbix-Introduction/7.png)

- CPU使用率恢復正常

![recovery](https://raw.githubusercontent.com/Charles-Miao/blog/master/static/Zabbix-Introduction/8.png)

- 通知（郵件通知/ 脚本通知）

## 其他應用

- 異常自動處理（重啓服務器/ 重啓服務/ 切換備份服務器等）
- Zabbix API二次開發（开发web 界面、开发手机端zabbix、获取zabbix 指定数据、创建zabbix 监控项等）
- 資產清單

![other](https://raw.githubusercontent.com/Charles-Miao/blog/master/static/Zabbix-Introduction/9.png)

## 參考資料

[Zabbix基礎監控項Keys介紹](https://fashengba.com/post/zabbix-item-keys.html)

[Zabbix通過SNMP監控HP Gen10服務器硬件](http://www.zmzblog.com/monitor/zabbix-how-to-monitoring-hp-gen10-server-hardware.html)

[HP ProLiant ML/DL/BL iLO2 - 管理控制器驅動程序和管理接](https://support.hpe.com/hpsc/doc/public/display?docld=c01851759)[口](https://support.hpe.com/hpsc/doc/public/display?docId=c01851759)[驅動](https://support.hpe.com/hpsc/doc/public/display?docld=c01851759)[程序如何工作](https://support.hpe.com/hpsc/doc/public/display?docId=c01851759)





