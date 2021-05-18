---
title: "Zabbix in Action - DL160 G6"
date: 2021-05-18T22:22:27+08:00
description: ""
draft: false
tags: [Zabbix,Linux,HP]
categories: [运维]
---

主要内容
---
- 背景说明
- 升级Windows Server 2012探索
- 升级CentOS 7探索
- 解决方案
- 其他说明

<!--more-->

背景说明
---
- 公司需求针对EOS OS（CenotOS-6和Windows Server 2008）进行系统升级
- DL160 G6升级系统后无法进行硬件监控

升级Windows Server 2012探索
---
- 惠普官网没有支持2012的驱动

升级CentOS-7探索
---
- 需要安装hp-snmp-agent、hp-health、hpacucli驱动，以及SNMP服务
- 惠普官网没有支持CentOS-7的驱动
- CentOS-6的hp-health和hpacucli驱动可以正常安装
- CentOS-6的hp-snmp-agent无法进行安装，查看报错信息发现hp-snmp-agent是基于低版本的snmp-5.5（CentOS-6）
- 进一步确认CentOS-7无法安装低版本的snmp-5.5，CentOS-7.9默认安装的是snmp-5.7

```shell
rpm -ivh XXX.rpm #安装rpm包
rpm -qa | grep "hp-health" #查询已经安装的hp-health软件包
rpm -e XXX.rpm --nodeps #卸载软件包
```

解决方案
---
- 温度，可以透过ipmi进行读值和监控，模板参考[template-ilo-100i](https://share.zabbix.com/cat-server-hardware/hp/template-server-hp-ilo100i-ipmi)，此模板基于Zabbix 4.0，参见item：Front Panel
- 风扇，可以透过ipmi进行读值和监控，模板参考[template-ilo-100i](https://share.zabbix.com/cat-server-hardware/hp/template-server-hp-ilo100i-ipmi)，此模板基于Zabbix 4.0，参见item：FAN1_INLET
- 内存，安装hp-health驱动，可以透过hpasmcli指令进行读值，可以透过自定义key进行监控
- CPU，安装hp-health驱动，可以透过hpasmcli指令进行读值，可以透过自定义key进行监控
- Powersupply，此型号PS只有一个，无法透过ipmi和hpasmcli进行读值，也不需要读值
- Disk，安装hpacucli驱动，可以透过指令hpacucli进行读值，可以透过自定义key进行监控

- DL160 G6安装最新版本的hp-health，会报[ERROR: Failed to get SMBIOS system ID.](https://community.hpe.com/t5/System-Administration/hpasmcli-not-working-after-update-to-Debian-Jessie-8-7/m-p/6942203#M54944)，退回旧版hp-health-9.50可以解决此error

- [hpacucli & hpasmcli管理工具介绍](http://www.361way.com/hpacucli/5890.html)
- [hpasmcli - How to use hpasmcli command on HP Proliant Server](https://cmdref.net/hardware/proliant/hpasmcli.html)

```shell
hpacucli ctrl all show config   #Raid和HDD状况
hpasmcli -s 'show dimm'         #查看内存信息
hpasmcli -s 'show TEMP'         #查看硬件温度
hpasmcli -s 'show fans'         #查看风扇信息
hpasmcli -s 'show powersupply'  #查看电源模块
hpasmcli -s 'show server'       #查看机器型号,序列号,CPU,内存大小
```

其他说明
---
- CentOS-6 EOS Date is 11/30/2020
- CentOS-7 EOS Date is 6/30/2024
- Windows Server 2008 EOS Date is 1/14/2020
- Windows Server 2012 EOS Date is 10/10/2023
- Windows Server 2020 EOS Date is 1/12/2027

- DELL2950、DELL2900和DL380 G7可以正常升级至Windows Server 2016，但是内存使用率会过高，需要关闭Windows defender，并将Windows Update改为手动更新，建议退回到Windows Server 2012
- DL380 G7升级到Windows Server 2016后无法监控内存信息，建议退回至Windows Server 2012
- DL380 G9和G10可以正常升级至Windows Server 2016