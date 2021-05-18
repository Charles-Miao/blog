---
title: "生产电脑智慧化管理 - 蓝图篇"
date: 2020-08-11T22:03:23+08:00
description: ""
draft: false
tags: [Windows, PC]
categories: [运维]
---
主要内容
---
- 专案背景
- 蓝图和构思
- 实战工具和方法
<!--more-->

背景
---

1. 日常需要手动维护
    
    - 手动安装系统、手动安装驱动、手动更新程序
    - 手动升级补丁、手动休眠和shutdown、现场手动处理电脑异常、手动检查officescan连接状况和电脑激活状况
    - 电脑基本信息、安全信息、系统性能、系统运行状况等数据全部需要手动确认和记录，无法透过电脑信息分析问题
    - 电脑故障无系统追踪，无法透过历史数据分析问题

2. 数位化，大势所趋
    
    - 各个工厂都在大力发展自动化线体，针对这种线体中的设备、治具、仪器、电脑等必定需要系统监控和自动化维护

蓝图
---

![blueprint](https://github.com/Charles-Miao/blog/blob/master/static/Host-PC-Monitoring/blueprint.PNG?raw=true)

- 首先，将电脑各种手动维护改为自动化维护
- 其次，使用系统监控电脑数据，并实现远程协助
- 最后，透过监控和历史数据对电脑进行更智能化的维护

实战
---

- 封装Windows image
    - 使用工具：EasySysprep
    - 参考连接：[https://cloud.tencent.com/developer/article/1438238](https://cloud.tencent.com/developer/article/1438238)

- 自动升级电脑补丁
    - 使用工具：WSUS

- 远程登录产线电脑，并协助处理问题
    - 使用工具：TightVNC
    - 使用方法：将VNC工具封装在电脑image中，透过监控系统获取电脑的IP信息，再透过服务器远程控制产线电脑

- 自动检查officescan和正版激活状况
    - 自定义开发工具：[https://github.com/Charles-Miao/Python-in-Action/tree/master/CheckComputer](https://github.com/Charles-Miao/Python-in-Action/tree/master/CheckComputer)
    - 透过监控系统实现闭环管理

- 电脑监控系统设计和开发
    - 实现监控电脑基本信息、安全信息、系统性能、系统运行状况等
    - 介绍连接：[https://charles-miao.github.io/post/Host-PC-Monitoring-2/](https://charles-miao.github.io/post/Host-PC-Monitoring-2/)

- 透过监控数据分析电脑问题
    - 使用工具和方法：R，相关性分析
    - 链接：[https://charles-miao.github.io/post/Host-PC-Monitoring-3/](https://charles-miao.github.io/post/Host-PC-Monitoring-3/)

- 自动化部署电脑系统、驱动和程式（待更新）
    - 使用工具和方法：Ansible、PXE备份还原、自定义系统开发

- 电脑故障追踪，协助分析问题（待完善）
    - 使用工具：Mantis，trac

- 电脑智慧化管理案例分享（待完善）

- 电脑自动休眠和shutdown（待完善）

