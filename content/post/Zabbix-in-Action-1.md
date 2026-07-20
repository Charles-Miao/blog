---
title: "Zabbix in Action - Windows"
date: 2019-11-21T10:38:09+08:00
description: ""
draft: false
tags: [Zabbix, Windows]
categories: [运维]
---

软硬件环境
---
- Server端：Ubuntu 16.04虚拟机
- Agent端：Windows Server，主要硬件有DL380 G7、DL380 G9、DL380 G10、DL160 G6、DELL2900、DELL2950、supermicro等
<!--more-->

Server tool安装&问题汇总
---
- zabbix agent、ntpdate、mail工具安装与配置
```shell
#agent安装和配置
sudo apt-get install zabbix-agent
sudo apt-get install zabbix-get
#安装时间同步工具
sudo apt-get install ntpdate
#安装发送mail工具
sudo apt-get install bsd-mailx
sudo apt-get install mailx
sudo apt-get install s-nail
sudo apt-get install mailutils
#配置发送mail工具
sudo vim /etc/s-nail.rc
#配置Zabbix发送mail脚本：/usr/lib/zabbix/alertscripts/send_mail.sh
echo "$3" | mail -s "$2" "$1"
```

- 无法抓取Client端数据，需要设定server端端口，并重启zabbix

```sheel
#手动设定端口:10051
vim /etc/zabbix/zabbix_server.conf
sudo /etc/init.d/zabbix-server restart
```

- [安装异常: The frontend does not match Zabbix database ](https://blog.csdn.net/purplegalaxy/article/details/37819899)

- 若为硬体服务器需要特别注意时间同步，需要确保Zabbix服务器的时间准确
```shell
# 时间同步
# crontab -l
00 00 * * * /usr/sbin/ntpdate -u 195.13.1.153
```

HP DL380系列服务器透过iLO口snmp协议进行硬件监控
---

- 系统需要开启SNMP服务，并在security选项卡中开放public只读功能
- 需要安装iLO 3/4 Channel Interface Driver
- 需要安装iLO 3/4 Management Controller Driver Package
- 需要安装HPE Insight Management Agents
- 需要安装Smart Array SAS/SATA Controller Driver，用于读取硬盘信息（**这个当时搞了好久**）
- OID查询：[http://oidref.com/1.3.6.1.4.1.3582.4.1.4.1.2.1.19](http://oidref.com/1.3.6.1.4.1.3582.4.1.4.1.2.1.19)
- HP服务器驱动查找：[https://support.hpe.com/hpesc/public/km/product/1009087943/hpe-proliant-dl380-gen9-server-models?ismnp=0&l5oid=7271241#t=DriversandSoftware&sort=relevancy&layout=table](https://support.hpe.com/hpesc/public/km/product/1009087943/hpe-proliant-dl380-gen9-server-models?ismnp=0&l5oid=7271241#t=DriversandSoftware&sort=relevancy&layout=table)

DL160 G6 & Supermicro透过ipmi & snmp协议进行硬件监控
---
- DL160 IPMI接口共用NIC1，需要將BMC NIC Allocation設定為Shared，賬號：admin，密碼：admin
- Supermicro IPMI接口有單獨的網卡，設定完之後需要**斷電重啓**，賬號：ADMIN，密碼：ADMIN
- Supermicro服務器透過SNMP協議監控HDD狀況（需要安裝MegaRAID Storage Manager）
- IOD查询：[https://mibs.observium.org/mib/LSI-MegaRAID-SAS-MIB/](https://mibs.observium.org/mib/LSI-MegaRAID-SAS-MIB/)
- Supermicro其他硬件信息透過ipmi協議獲取
```
ipmitool -I lanplus -H 192.168.123.149 -U ADMIN -P ADMIN sensor list
ipmitool -I lanplus -H 192.168.123.149 -U ADMIN -P ADMIN sensor get "P1-DIMM3B Temp"
```
DELL服务器硬件监控
---
DELL服务器因为过旧，都没有安装带外管理的卡，所以硬件监控全部是透过自定key的方式实现的

- 服务器需要安装OMSA管理工具
- python脚本参见：[https://github.com/Charles-Miao/Server-Monitoring/tree/master/Ver2.0/zabbix/Windows/Zabbix/dell](https://github.com/Charles-Miao/Server-Monitoring/tree/master/Ver2.0/zabbix/Windows/Zabbix/dell)

Windows服务器一些特殊信息获取
---
因为有很多信息客户端无法获取到，所以需要自己写自定义key，有些指令因为处理时间较长，需要透过Sender的方式进行获取
- python脚本参见：[https://github.com/Charles-Miao/Server-Monitoring/tree/master/Ver2.0/zabbix/Windows/Zabbix/windows](https://github.com/Charles-Miao/Server-Monitoring/tree/master/Ver2.0/zabbix/Windows/Zabbix/windows)


Zabbix web端配置模板
---
- 详细参见：[https://github.com/Charles-Miao/Server-Monitoring/tree/master/Ver2.0/zabbix/template](https://github.com/Charles-Miao/Server-Monitoring/tree/master/Ver2.0/zabbix/template)