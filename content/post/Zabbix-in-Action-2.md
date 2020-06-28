---
title: "Zabbix in Action - Linux"
date: 2020-06-28T11:53:17+08:00
description: ""
draft: false
tags: [Zabbix, Linux]
categories: [运维]
---
主要讲解RHEL 5如何安装和配置agent & snmp协议，以及如何实现HP DL160 G6的硬件监控
<!--more-->

Download [zabbix agent](https://repo.zabbix.com/zabbix/3.2/rhel/5/x86_64/) rpm package 
---
- zabbix-agent
- zabbix-get
- zabbix-sender

Zabbix agent install & config
---

```shell
rpm -ivh zabbix-agent-3.2.0-1.el5.i386.rpm --force --nodeps #install agent
vim /etc/zabbix/zabbix_agentd.conf #setting config file
zabbix_agentd -c /etc/zabbix/zabbix_agentd.conf #start agent
vi /etc/rc.local #add to startup
/etc/init.d/zabbix-agent restart #add to startup
```

Search [snmp](http://rpm.pbone.net/) rpm package
---
- lm_sensors-3.0.2-1centos5.i386.rpm
- net-snmp-5.4.2-4centos5.i386.rpm
- net-snmp-devel-5.4.2-4centos5.i386.rpm
- net-snmp-libs-5.4.2-4centos5.i386.rpm
- net-snmp-utils-5.4.2-4centos5.i386.rpm

Install & config snmp service
---
- [Centos7 安装snmp](https://www.jianshu.com/p/1293ca633995)
- [CentOS下SNMP服务安装](https://blog.51cto.com/907832555/1953617)

[Zabbix通过SNMP监控HP服务器硬件信息](https://blog.51cto.com/sfzhang88/1595211)
---
- hpacucli-9.40-12.0.x86_64.rpm
- hp-snmp-agents-9.40-2506.37.rhel6.x86_64.rpm
- hp-health-9.40-1602.44.rhel6.x86_64.rpm


其他知识
---
- 在使用ftp传输时，需要将传输模式改为二进位模式

```shell
open x.x.x.x #打开并登录ftp
image #設定二進位傳輸模式(同binary)
mget #傳輸多個遠端檔案
quit #離開ftp會話
```
