---
title: "Linux基础 - Part5"
date: 2021-06-07T23:19:19+08:00
description: ""
draft: false
tags: [Linux]
categories: [运维]
---
# 主要内容

- 备份服务器
- 存储服务器
- 实时同步服务

<!--more-->

> [详细笔记](https://github.com/Charles-Miao/Linux/blob/master/Linux%E5%9F%BA%E7%A1%80/%E7%AC%94%E8%AE%B027~31.txt)

## 备份服务器

### rsync软件使用方法
```shell
#rsync软件使用方法
rsync /etc/hosts /tmp #替代本地备份cp指令
rsync -rp /etc/hosts root@172.16.1.41:/backup #替代远程备份scp指令
rsync -rp /oldboy 172.16.1.41:/backup #备份目录没有斜线，备份目录自身
rsync -rp /oldboy/ 172.16.1.41:/backup #备份目录有斜线，备份目录下面的子文件
rsync -rp --delete /null/ 172.16.1.41:/backup #镜像同步，删除速度比rm指令快
rsync /etc/hosts #替代ls指令,查看此文件
```

### rsync守护进程模式搭建
```shell
#1. 下载安装软件
rpm -qa | grep rsync
yum install -y rsync
#2. 编写配置文件
vim /etc/rsyncd.conf

uid = rsync			#指定管理备份目录的用户
gid = rsync			#指定管理备份目录的用户组
port = 873			#定义rsync备份服务的网络端口号
fake super = yes			#将rsync虚拟用户伪装为一个超级管理员用户
use chroot = no			#和安全相关的配置
max connections = 200		#最大连接数
timeout = 300			#超时时间（单位sec）
pid file = /var/run/rsyncd.pid		#进程号码信息：1. 可以快速kill进程（kill `cat /var/run/rsyncd.pid`）；2. 判断一个服务是否正常运行
lock file = /var/run/rsync.lock		#锁文件
log file = /var/log/rsyncd.log		#日志文件
ignore errors			#忽略简单错误
read only = false			#指定备份目录可读可写
list = false			#禁止客户端list出所有模块（rsync rsync_backup@172.16.1.41::）
hosts allow = 172.16.1.0/24		#白名单
hosts deny = 0.0.0.0/32		#黑名单
auth users = rsync_bakcup		#指定认证用户
secrets file = /etc/rsync.password	#认证用户密码文件（用户和密码信息）
[backup]				#模块信息
comment = "backup dir by charles"	
path = /backup			#模块中配置参数，指定备份目录

#3. 创建rsync服务的虚拟用户
useradd rsync -M -s /sbin/nologin

#4. 创建备份服务认证密码文件
echo "rsync_backup:241668@WSX" > /etc/rsync.password
chmod 600 /etc/rsync.password

#5. 创建备份目录并修改属主属组信息
mkdir /backup
chown rsync.rsync /backup/

#6. 启动并设定开机运行
systemctl start rsyncd
systemctl enable rsyncd

#7. 测试
rsync -avz /etc/hosts rsync_backup@172.16.1.41::backup

# 客户端配置

#1. 创建密码文件
echo "241668@WSX" > /etc/rsync.password
chmod 600 /etc/rsync.password

#2. 进行免交互传输数据测试
rsync -avz /etc/hosts rsync_bakcup@172.16.1.41::backup --password-file=/etc/rsync.password
```

### rsync命令的常用参数
```shell
# -v，显示详细传输信息
# -a，命令的归档参数，包含rtopgDl参数
# -r，递归参数
# -t，保持文件属性信息时间信息不变（修改时间）
# -o，保持文件属主信息不变
# -g，保持文件属组信息不变
# -p，保持文件权限信息不变
# -D，保持设备文件信息不变
# -l，保持链接文件属性不变
# -L，保持链接文件数据信息不变
# -P，显示文件传输进度
# --exclude=PATTERN，排除指定数据不被传输
# --exclude-from=file，排除指定数据不被传输（批量排除）
# --bwlimit=RATE，限制传输的速率
# --delete，镜像同步
```

### 企业应用rsync技巧
```shell
# 1. 添加多模块，可以让不同部门的资料拷贝到不同目录中
# 2. 排除功能，--exclude-from=file
# 3. 直接在备份服务器穿件备份目录，不同服务器备份到不同目录
rsync -avz /etc/hosts rsync_bakcup@172.16.1.41::backup/172.16.1.21/ --password-file=/etc/rsync.password
# 4. 守护进程的访问限制
# 4.1 只有白名单，除了白名单之外的都不能传
# 4.2 只有黑名单，除了黑名单之外的都能传
# 4.3 有白名单和黑名单，除了黑名单之外的都能传
# 4.4 白名单优先级高于黑名单
# 5. 禁止客户端list出所有模块（rsync rsync_backup@172.16.1.41::）
list = false
```

### 企业全网备份项目 

```shell
#客户端：
mkdir -p /backup/10.0.0.31/

cd / #使用相对路径，绝对路径会有提示
tar zchf /backup/10.0.0.31/system_backup_$(date +%F_week%w).tar.gz ./var/spool/cron/root ./etc/rc.local ./server/scripts ./etc/sysconfig/iptables
tar zchf /bakcup/10.0.0.31/www_backup_$(date +%F_week%w).tar.gz ./var/html/www
tar zchf /bakcup/10.0.0.31/www_log_bakcup_$(date +%F_week%w).tar.gz ./app/logs
#补充：tar命令-h参数，将连接文件所指向的源文件进行保存备份

find /bakcup -type f -mtime +7 | xargs rm #删除旧文件

find /backup/ -type f -mtime -1 ! -name "finger*" |xargs md5sum >>/backup/10.0.0.31/finger.txt #生成指纹文件

rsync -avz /backup/ rsync_backup@172.16.1.41::backup --password-file=/etc/rsync.password

#服务端：
mkdir -p /backup

find /backup/ -type f -mtime +180 ! -name "*week1.tar.gz" #删除180天前，并排除周一的数据

find /backup/ -type f -name "finger.txt" | xargs md5sum -c #进行md5验证

# 发送邮件
#1. 编写liunx服务邮件相关配置文件
vim /etc/mail.rc
set from=fengkuang33@163.com smtp=smtp.163.com
set smtp-auth-user=邮箱账号 smtp-auth-password=登录邮箱密码 smtp-auth=login
systemctl restart postfix.service
#2. 发送邮件测试
echo "邮箱发送测试" | mail -s "邮箱测试" 1017635452@qq.com
mail -s "邮箱测试" 1017635452@qq.com < /temp/check.txt

# 编写脚本
sh -x backup.sh #显示执行过程
hostname -i #获取内网地址
hostname -I #获取所有地址

# client端：
#!/bin/bash
Backup_dir="/backup"
IP_info=$(hostname -i)
#create backup dir
mkdir -p $Backup_dir/$IP_info
#tar backup data
cd /
tar zchf $Backup_dir/$IP_info/system_backup_$(date +%F_week%w).tar.gz ./var/spool/cron/root ./etc/rc.local ./server/scripts ./etc/sysconfig/iptables
#del 7 day ago data
find $Backup_dir -type f -mtime +7 | xargs rm 2>/dev/null
#create finger file
find $Backup_dir/ -type f -mtime -1 ! -name "finger*" | xargs md5sum >$Backup_dir/$IP_info/finger.txt
#backup push data info
rsync -az $Backup_dir/ rsync_backup@172.16.1.41::backup --password-file=/etc/rsync.password

# server端：
#!/bin/bash
#del 180 day ago data
find /backup/ -type f -mtime +180 ! -name "*week1.tar.gz" | xargs rm 2>/dev/null
#check backup data
find /backup/ -type f -name "finger.txt" | xargs md5sum -c >/tmp/check.txt
#send check mail
mail -s "check backup info for $(date +%F)" 1017635452@qq.com < /tmp/check.txt

# 定时任务
#client端：
crontab -e
0 0 * * * /bin/sh /server/scripts/backup.sh &>/dev/null
#server端：
0 5 * * * /bin/sh /server/scripts/backup_server.sh &>/dev/null
```
## 存储服务器

### nfs服务介绍
```shell
# NFS是Network file system缩写，即网络文件共享系统
# 中小型企业：FTP、samba（windows-linux）、NFS（linux-linux）
# 大型企业：分布式存储（FastDFS，GlusterFS，Moosefs）
```

### NFS部署流程
```shell
# 服务端部署：
# 1. 检查和安装
rpm -qa | grep -E "nfs|rpc"
yum install -y nfs-utils rpcbind
# 2. 编写nfs配置文件
vim /etc/exports
#路径	白名单（权限）
/data	172.16.1.0/24(rw,sync)
# 3. 创建存储目录
mkdir /data
chown nfsnobody.nfsnobody /data
# 4. 启动服务程序
# 先启动rpc
systemctl start rpcbind.service
systemctl enable rpcbind.service
# 后启动nfs
systemctl start nfs
systemctl enable nfs

# 客户端部署：
yum install -y nfs-utils 
mount -t nfs 172.16.1.31:/data /mnt
```
### nfs服务端详细配置说明
```shell
# 1. 多网段主机进行挂载
#方法一
/data 172.16.1.0/24(rw,sync) 10.0.0.0/24(rw,sync)
#方法二
/data 172.16.1.0/24(rw,sync)
/data 10.0.0.0/24(rw,sync)

# 2. nfs配置参数权限
# rw，读写权限
# ro，只读权限
# sync，同步方式存储，直接写入磁盘（安全）
# async，异步方式存储，数据放在内存中，慢慢写进磁盘（效率）
# no_root_squash，不要将root用户身份进行转换（存储文件时，文件的属主属组信息转换）
# root_squash，将root用户身份进行转换为nfsnobody（存储文件时，文件的属主属组信息转换）
# all_squash，将所有用户身份进行转换为nfsnobody（存储文件时，文件的属主属组信息转换）
# no_all_squash，不要将普通用户身份进行转换（存储文件时，文件的属主属组信息转换）

# 3. 确保数据的安全性（也是默认配置）：
# no_all_squash	需要进行配置	共享目录权限为www（只有www用户可以操作此目录，客户端和服务端www账号的uid必须一样）
# root_squash	需要进行配置	data目录的属主为www，nfsnobody无法操作（root无法操作此目录）

# 4. 如何让root用户可以操作管理www用户管理的data目录
# anonuid，anongid，可以指定映射用户信息
# 修改映射用户为www（uid=1002），不要设定nfsnobody
# /data 172.16.1.0/24(rw,sync,anonuid=1002,anongid=1002)

# 5. nfs共享目录的权限和下列因素相关
# 5.1 目录本省权限
# 5.2 和配置文件中的权限配置相关（rw/ro xxx_squash anonuid anongid）
# 5.3 和客户端挂载命令的参数有关（mount -o ro，只读）

# 6. 服务重启方式：
# 6.1 restart，强制断开所有连接
# 6.2 reload，强制断开没有数据传输的连接（建议使用）
```

### nfs客户端详细配置说明
```shell
# 1. 自动挂载
# 1.1 利用rc.local
mount -t nfs 172.16.1.31:/data /mnt
# 1.2 利用fstab文件（centos7必须开机启动remote-fs.target，centos6必须开机启动netfs）
172.16.1.31:/data		/mnt		nfs		default		0	0
# centos7查看开机启动服务：ll /etc/systemd/system/multi-user.target.wants/

# 2. mount命令参数
# rw，实现挂载后挂载点目录可读可写（默认）
# ro，实现挂载后挂载点目录只读
# suid，在共享目录中可以让setuid权限位生效（默认）
# nosuid，在共享目录中可以让setuid权限位失效，提高安全性
# exec，共享目录中的执行文件可以直接执行
# noexec，共享目录中执行文件可以无法直接执行，提高安全性
# auto，可以实现自动挂载，mount -a实现加载fstab文件自动挂载，无需重启
# noauto，不可以实现自动挂载
# nouser，禁止普通用户卸载挂载点
# user，运行普通用户卸载挂载点

umount -lf /mnt #强制卸载，-l不退出挂载点，-f强制
```
### NFS服务挂载不上排查方法
```shell
# 服务端：
# 1. 检查nfs进程信息是否注册，服务启动顺序不对，没有启动nfs
rpcinfo -p localhost
# 2. 检查有没有可用存储目录，配置文件编写有问题，重启nfs
showmount -e 172.16.1.31
# 3. 在服务端进行挂载测试，是否能够在存储目录中创建或删除数据
# 客户端：
# 1. 检查nfs进程信息是否注册，服务启动顺序不对，没有启动nfs
rpcinfo -p localhost
# 2. 检查有没有可用存储目录，配置文件编写有问题，重启nfs
showmount -e 172.16.1.31
ping 172.16.1.31
telnet 172.16.1.31 111
```
## 实时同步服务

```shell
#原理（rsync备份数据、inotify监控目录是否变化、sersync实时同步）

# - 方法
# 1. rsync部署
# 2. inotify部署
# 2.1 yum install -y inotify-tools
# 2.2 inotifywait命令使用方法

-m #实现一直监控目录的数据变化
-r #进行递归监控
-q #quiet，尽量减少信息输出
--format <fmt> #指定输出信息的格式
--timefmt #指定输出的时间信息格式
-e #指定监控的事件信息
inotifywait -mrq --timefmt "%F" --format "%T %w %f %e" /data -e CREATE
#create创建、delete删除、moved_to移入、close_write修改
#企业应用，防止系统重要文件被破坏

# 3. sersync部署
# 3.1 下载安装，并上传至linux服务器中
# https://github.com/wsgzao/sersync
# rz -y
# 3.2 解压
unzip sersync_installdir_64bit.zip
mv sersync_installdir_64bit/sersync/ /usr/local/ 
# 3.3 编写配置文件
vim conf/confxml.xml
# 3.4 启动sersync程式
# 把/usr/local/sersync/bin加入环境变量$PATH
# 参数-d，启动守护进程模式
# 参数-r，在监控前，将监控目录与远程主机用rsync命令推送一遍
# 参数-o，指定配置文件
sersync -dro /usr/local/sersync/conf/confxml.xml #启动实时同步服务
yum provides killall #查看killall指令属于哪个包
yum install -y psmisc
killall sersync #停止实时同步服务
/etc/rc.local <-- sersync -dro /usr/local/sersync/conf/confxml.xml #实现开机自启动
```
