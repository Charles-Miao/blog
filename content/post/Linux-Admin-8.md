---
title: "Linux基础 - Part8"
date: 2021-06-28T23:19:54+08:00
description: ""
draft: false
tags: [Linux]
categories: [运维]
---
# 主要内容
- 监控内容
- 系统监控指令
- 报警媒介

<!--more-->

> [详细笔记](https://github.com/Charles-Miao/Linux/blob/master/Linux%E5%9F%BA%E7%A1%80/%E7%AC%94%E8%AE%B044~45.txt)

## 监控内容

```shell
# 1. 硬件监控，服务器、路由器、交换机、防火墙（snmp）
# 2. 系统监控，CPU 内存 磁盘 网络 进程 TCP（十一种状态）
# 3. 服务监控，nginx php tomcat Redis memcache mysql
# 4. 网站监控，请求时间 响应时间 加载时间 页面监控
# 5. 日志监控，ELK 日志易
# 6. 安全监控，Firewalld（4层和4层以上）WAF（nginx+lua）（应用层面）安全宝 牛盾云 安全狗
# 7. 网络监控，smokeping 监控宝 站长工具 奇云测 多机房
# 8. 业务监控，活动产生多少流量 产生多少注册量 带来多少价值
```

## 系统监控指令

```shell
# CPU：top htop glances
# us：user state	用户态信息	40%
# sy：system state	内核态信息	40%
# idle		空闲状态		20%

# 内存：top htop free
# 内存可用率
# swap空间使用情况

# 磁盘：df iotop glances
# 磁盘使用情况
# 磁盘的IO消耗

# 网络：iftop glances
# 带宽使用情况

# 进程：top htop ps glances
# 占用内存比较多的内存

# 负载：w top uptime glances
# 10分钟负载 <CPU内核数
# 15分钟负载 <CPU内核数
```

## 报警媒介
### 微信报警：
```shell
# 1. 注册企业微信，并配置
# 01. 获取企业ID
# 02 允许员工加入
# 03 应用小程序（创建、agentid、secret）

# 2. 编写脚本，python，网上下载

# 3. 报警媒介配置
```
### 短信和电话：
```shell
# 1. 利用阿里大鱼（收费）
# 2. onealert
```