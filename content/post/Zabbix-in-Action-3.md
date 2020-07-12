---
title: "Zabbix in Action - Grafana"
date: 2020-07-07T22:25:58+08:00
description: ""
draft: false
tags: [Zabbix, Grafana]
categories: [运维]
---
Outline
---
- Grafana+Zabbix
- 文件同步监控实战（Grafana+MySQL）
- MySQL配置
<!--more-->

Grafana+Zabbix
---
- Grafana是一个跨平台的开源的度量分析和可视化工具，可以通过将采集的数据查询然后可视化的展示，并及时通知
- Grafana安装和配置都比较简单，而且网上的资料也很多，这里就忽略了

文件同步监控实战（Grafana+MySQL）
---
- Zabbix每天定时运行此自定义key脚本
- python脚本判断文件同步是否正常，并将结果insert into MySQL数据库，详细判断逻辑请参考check_sync_result函数
- Grafana从MySQL中抓取数据，并展示文件同步结果

```python
#脚本功能：
#1. 实现自定义key
#2. 将文件同步检查结果insert into MySQL数据库
import os
import re
import time
import pymysql
import datetime
import configparser


def check_sync(path,string):
	check_sync_result=0
	read_log=open(path,mode='r',encoding='UTF-8')
	conent=read_log.readlines()
	for index in range(len(conent)):
		if string in conent[index]:
			check_sync_result=1
	read_log.close()
	return(check_sync_result)
	
def get_sync_date(path):
	info = os.stat(path)
	time_local=time.localtime(info.st_mtime)
	file_change_date=time.strftime("%Y-%m-%d",time_local)
	return(file_change_date)

def check_sync_result():
	config=configparser.ConfigParser()
	config.read(r"C:\Zabbix\windows\server_info.ini")
	items=config.items("Sync_Path")
	
	sync=[]
	for index in range(len(items)):
		path_list=re.split(r'[,]',items[index][1])
		#skip empty path
		if str(items[index][1])=="":
			pass
		#if not exist sync result log, sync result is 0
		elif os.path.exists(path_list[0].strip())==False:
			sync.append(0)
		#if sync log is not today, sync result is 0
		elif str(get_sync_date(path_list[0].strip()))!=str(datetime.date.today()):
			sync.append(0)
		#if sync log not contains pass result, sync result is 0
		elif check_sync(path_list[0].strip(),path_list[1].strip())==0:
			sync.append(0)
		else:
			sync.append(1)
	return(sync)
	
if __name__ == '__main__':
	#check sync result
	sync=check_sync_result()
	sync_total=0
	for index in range(len(sync)):
		sync_total=sync_total+sync[index]
	if sync_total<len(sync):
		sync_result=0
	else:
		sync_result=1
	#get now time
	now_time=time.strftime("%Y-%m-%d %H:%M:%S"),time.localtime()
	now_time_string="\'"+str(now_time[0])+"\'"
	#get server ip
	config=configparser.ConfigParser()
	config.read(r"C:\Zabbix\windows\server_info.ini")
	IP=config.get("Server_Info","Back_IP")
	IP_string="\'"+str(IP)+"\'"
	#insert into db
	sql="INSERT INTO SYNCTABLE (IP, TIME, SYNC_STATUS) VALUES (%s,%s,%s)" % (IP_string,now_time_string,sync_result)
	db=pymysql.connect("192.168.123.211","root","password","SYNCFILES")
	cursor=db.cursor()
	cursor.execute(sql)
	db.commit()
	db.close()
	#print sync result
	print(sync_result)
```

MySQL配置
---
- Agent需要安装pymysql模块，下载地址：https://github.com/pymysql/pymysql
```shell
#安装指令
python setup.py install
```
- 命令行登录MySQL数据库
```shell
mysql -h localhost -u root -p
password
```
- 配置MySQL，以便agent能够远程操作数据库
```shell
#配置mysql配置档，注释掉如下内容
sudo vim /etc/mysql/mysql.conf.d/mysqld.cnf
# bind-address = 127.0.0.1

#关闭防火墙
sudo ufw disable

#赋给用户远端权限
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'password' WITH GRANT OPTION;

FLUSH PRIVILEGES;
```