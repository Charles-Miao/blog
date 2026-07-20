---
title: "Zabbix自定义Key读值为空"
date: 2021-05-19T22:15:08+08:00
description: ""
draft: false
tags: [Zabbix,apacucli,Python,Linux]
categories: [运维]
---

主要内容
---
- 问题说明
- 分析思路
- 解决方案

<!--more-->

问题说明
---
- 透过[Python脚本](https://github.com/Charles-Miao/Server-Monitoring/tree/master/Ver2.0/zabbix/CentOS-7)调用hpacucli指令读取硬件信息，本地可以正常读取硬件信息，zabbix server端透过zabbix_get指令读值为空

分析思路
---
- Google[自定义脚本获取key失败怎么办？](https://www.yuanmas.com/info/rgzEoJ5Ay8.html)，赋予zabbix账号管理员权限，现象依旧
- 调整配置档案zabbix_agent.conf中的debuglevel参数，默认为3只显示warning信息，4为debug模式，透过debug log（/var/log/zabbix）发现，指令执行没有特别异常，现象依旧（此时已崩溃，Google无解，debug log无解）

```text
  4752:20210519:153212.560 Requested [hp.pdisk_discovery]
  4752:20210519:153212.560 In zbx_popen() command:'python /etc/zabbix/hp/pdisk_discovery.py'
  4752:20210519:153212.561 End of zbx_popen():7
  4841:20210519:153212.561 zbx_popen(): executing script
  4752:20210519:153212.666 In zbx_waitpid()
  4752:20210519:153212.667 zbx_waitpid() exited, status:0
  4752:20210519:153212.667 End of zbx_waitpid():4841
  4752:20210519:153212.667 EXECUTE_STR() command:'python /etc/zabbix/hp/pdisk_discovery.py' len:12 cmd_result:'{"data": []}'
  4752:20210519:153212.667 Sending back [{"data": []}]
```

- 调试python脚本，发现使用zabbix账号调用hpacucli指令时，此指令未正常运行，无任何报错
- 使用admin账号執行hpacucli指令提示：**Error: You need to have administrator rights to continue.**
- 赋予admin管理员权限，并使用sudo hpacucli可以正常执行指令

```shell
visudo #赋予admin权限，可执行所有指令，并无需输入password
admin ALL=(root) NOPASSWD: ALL
```

解决方案
---
- visudo，賦予zabbix管理員權限
```shell
zabbix ALL=(root) NOPASSWD: ALL
```
- 使用**sudo hpacucli**指令运行
