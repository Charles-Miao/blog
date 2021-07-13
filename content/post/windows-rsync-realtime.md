---
title: "Windows实时同步文件至NAS"
date: 2021-07-13T22:58:21+08:00
description: ""
draft: false
tags: [Windows, NAS, rsync, Python]
categories: [运维]
---
# 主要内容
- 问题说明
- 环境部署
- 脚本实现

<!--more-->

## 问题说明

- 需要将windows系统中的测试log（小而多）实时拷贝至NAS Server共享目录
- Windows中缺乏开源免费的工具（sersync）实时同步测试log，robocopy适合做增量定期备份，Second Copy等软件都为收费软件

## 环境部署

- **NAS Server开启rsync服务**，并配置/etc/rsync.conf
- Windows Server安装inotifywait，地址：https://github.com/thekid/inotify-win
- Windows Server**安装windows版rsync**，下载地址：https://www.itefix.no/i2/cwrsync
- **watchdog模块**，透过python直接监控文件目录变化，此模块跨平台
- **Paramiko模块**，透过python直接ssh登陆系统，并下系统指令
- **threading模块**，实现多进程
- **queue队列模块**

## 脚本实现

### 简单实现

- 监控目录变更频次底时运行无异常，文件夹变动频次高时无法记录所有变更，导致无法同步所有文件，最终需要引入多进程+列表才能解决此问题
- windows系统指令inotifywait没有很好的办法将回显信息加入python队列中，最终引进watchdog模块+queue模块解决此问题
- 处理效率底，需要引进多进程theading模块
- ssh免密登陆频次过高时会导致登陆失败和命令执行失败，需要增加延迟，加大linux的默认连接数/etc/ssh/ssh_conf，同时引进Paramiko模块

```python
#-*- coding: utf-8 -*-
import subprocess
import os
import time
import re

rsyncSrc=r'D:\Debug_Log'
rsyncDes='rsync_backup@192.168.123.42::realtime'
#中间以@间隔，方便后面提取文件名，若以空格间隔，会导致包含空格的文件名提取异常
listen=r'inotifywait -mrq --format "%%e@%%w\%%f" "D:\Debug_Log"'
popen=subprocess.Popen(listen,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)

while True:
    line=popen.stdout.readline().strip()
    lineArr=line.decode().split('@')
    #获取监控的事件
    oper=lineArr[0]
    #获取变动路径
    file=lineArr[1]
    touched=False
    delete=False
    if file.index(rsyncSrc)==0:
        if (oper=='DELETE') or  (oper=='MOVED_FROM'):
            #转换路径
            _cureent_file=file.replace(rsyncSrc,'/cygdrive/d/Debug_Log')
            cureent_file=_cureent_file.replace('\\','/')
            #透过ssh免密的方式删除NAS Server上的内容
            delete_cmd='ssh administrator@192.168.123.42 \'rm -rf \"/volume1/Real-time'+cureent_file+'\"\''
            #获取文件修改时间
            #modify_time_cmd='ssh administrator@192.168.123.42 \'stat \"/volume1/Real-time'+cureent_file+'\"\''
            delete=True
        if (oper=='MOVED_TO') or (oper=='CREATE') or (oper=='MODIFY'):
            #转换路径
            _cureent_file=file.replace(rsyncSrc,'/cygdrive/d/Debug_Log')
            cureent_file=_cureent_file.replace('\\','/')
            #透过rsync将文件同步至NAS Server，密码存在pass.txt文件中
            rsync_cmd='rsync -avz -R -d --port=873 --delete --progress "'+cureent_file+'" '+rsyncDes+' --password-file="/cygdrive/d/ServerCheck/rsync/pass.txt"'
            touched=True
    if delete:
        #当天的文件被删除则同步删除NAS Server中文件，若是昨天之前的文件则不删除
        #conent=os.popen(modify_time_cmd).readlines()
        #modify_date=""
        #for index in range(len(conent)):
        #    if "Modify" in conent[index]:
        #        modify_date=re.split(r'[: ]',conent[index])[2].strip()		
        #if modify_date==time.strftime("%Y-%m-%d", time.localtime()):
        #    os.popen(delete_cmd)
        os.popen(delete_cmd)
    if touched:
        rsyncAction=os.popen(rsync_cmd)
        rsyncStat=rsyncAction.read()
        if "speedup is" in rsyncStat:
            print(file+' rsynced!')
            print(rsyncStat)
        else:
            print(file+' rsync failed!')
            print(rsyncStat)
```

### 多进程实现

- 解决第一个脚本中的所有问题

```python
import os
import logging
import queue
import threading
import time
import watchdog.observers as observers
import watchdog.events as events
import paramiko

logger = logging.getLogger(__name__)

SENTINEL = None
#获取CPU核数，以便设定进程池大小
def get_CPU_NumberOfCores():
	conent=os.popen("wmic cpu get NumberOfCores").readlines()
	CPU_NumberOfCores=0
	for index in range(len(conent)):
		if conent[index].strip()=="":
			continue
		elif conent[index].strip()=="NumberOfCores":
			continue
		else:
			CPU_NumberOfCores=CPU_NumberOfCores+int(conent[index].strip())
	return(str(CPU_NumberOfCores))        
#将事件加入列表
class MyEventHandler(events.FileSystemEventHandler):
    def on_any_event(self, event):
        super(MyEventHandler, self).on_any_event(event)
        queue.put(event)
    def __init__(self, queue):
        self.queue = queue
#根据不同的事件对文件做相应处理
def process(queue):
    while True:
        event = queue.get()
        logger.info(event)
        _current_file=(event.key)[1].replace(rsyncSrc,'/cygdrive/d/Debug_Log')
        current_file=_current_file.replace('\\','/')
        #创建或修改文件，则进行同步
        if ((event.key)[0] == "created" or (event.key)[0] == "modified") and (event.key)[2] == False:
            rsync_cmd='rsync -avz -R -d --port=873 --delete --progress "'+current_file+'" '+rsyncDes+' --password-file="/cygdrive/d/ServerCheck/rsync/pass.txt"'
            os.popen(rsync_cmd)	
        #若删除本地文件，则删除NAS服务器中的相应文件		
        elif (event.key)[0] == "deleted":
            #使用paramiko模块进行处理
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname='192.168.123.42', port=22, username='administrator', password='XXX')
            stdin, stdout, stderr = client.exec_command('rm -rf "/volume1/Real-time'+current_file+'"')
            client.close()
        #若修改文件名，则删除旧文件，同步新文件
        elif (event.key)[0] == "moved":
            #删除旧文件
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname='192.168.123.42', port=22, username='administrator', password='Z900TE@Quality!!#')
            stdin, stdout, stderr = client.exec_command('rm -rf "/volume1/Real-time'+current_file+'"')
            client.close()
            #获取新文件名，并进行同步
            _new_file=(event.key)[2].replace(rsyncSrc,'/cygdrive/d/Debug_Log')
            new_file=_new_file.replace('\\','/')
            rsync_cmd='rsync -avz -R -d --port=873 --delete --progress "'+new_file+'" '+rsyncDes+' --password-file="/cygdrive/d/ServerCheck/rsync/pass.txt"'
            os.popen(rsync_cmd)	
        #时间间隔7sec，防止内存和cpu过高
        time.sleep(7)

if __name__ == '__main__':

    rsyncSrc=r'D:\Debug_Log'
    rsyncDes='rsync_backup@192.168.123.42::realtime'
    #记录日志
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s %(threadName)s] %(message)s',
                        datefmt='%H:%M:%S')
    #列表
    queue = queue.Queue()
    #获取cpu核数，用于定义进程池大小
    num_workers = int(get_CPU_NumberOfCores())
    #将列表中的事件取出，逐一进行处理
    pool = [threading.Thread(target=process, args=(queue,)) for i in range(num_workers)]
    for t in pool:
        t.daemon = True
        t.start()
    #将文件变更的事件记录到列表中
    event_handler = MyEventHandler(queue)
    observer = observers.Observer()
    observer.schedule(
        event_handler,
        path=rsyncSrc,
        recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
```

## 参考连接
- [Windows下inotifywait和rsync全自动同步](http://blog.phpdr.net/windows%E4%B8%8Binotifywait%E5%92%8Crsync%E5%85%A8%E8%87%AA%E5%8A%A8%E5%90%8C%E6%AD%A5.html)，提供基本思路，实现部分主要体现在第一个脚本中
- [WINDOWS下INOTIFY+RSYNC实现实时备份](https://sre.ink/windows-inotify-rsync/)，第一个脚本主要参见这个python脚本
- [群晖 Nas 使用 SSH Key 实现免密登录](https://dryyun.com/2019/01/08/synology-nas-login-with-ssh-key/)，第一个脚本中ssh免密登陆参照此博文设定
- [Win配置免密ssh登录错误bad permissions](https://kknews.cc/code/p5knlze.html)，Windows中ssh免密登陆失败问题参照此博文修改
- [python中watchdog文件监控与检测上传](https://blog.csdn.net/submarineas/article/details/109363727)，使用watchdog模块替换inotifywait工具，多进程代码主要参照这个博文代码
- [Python模块学习 - Paramiko](https://www.cnblogs.com/xiao-apple36/p/9144092.html)，使用Paramiko模块替换ssh免密登陆指令