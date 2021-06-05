---
title: "Linux基础 - Part3"
date: 2021-05-26T22:34:12+08:00
description: ""
draft: false
tags: [Linux]
categories: [运维]
---

# 主要内容

- 系统启动流程
- 权限配置
- 用户相关文件和指令
- 定时服务
- 磁盘管理
- 其他知识

<!--more-->

> [详细笔记](https://github.com/Charles-Miao/Linux/blob/master/Linux%E5%9F%BA%E7%A1%80/%E7%AC%94%E8%AE%B020~24.txt)

## 系统启动流程

- CentOS6
```shell
#1. 加电自检
#2. mbr引导，读取磁盘的mbr存储记录信息，引导系统启动
#3. grub菜单，选择启动的内核，进行单用户模式重置密码
#4. 加载系统内核信息，可以更好的使用内核控制硬件
#5. 第一个进程运行起来 init
#6. 加载系统运行级别/etc/inittab
#7. 初始化脚本运行，初始化系统主机名称和网卡信息
#8. 运行系统特殊脚本，服务运行的脚本
#9. 运行mingetty进程，显示登陆界面
```

- CentOS7
```shell
#1. 加电自检
#2. mbr引导，读取磁盘的mbr存储记录信息，引导系统启动
#3. grub菜单，选择启动的内核，进行单用户模式重置密码
#4. 加载系统内核信息，可以更好的使用内核控制硬件
#5. 第一个进程运行起来 systemd（服务启动时，同时一起启动）
#6. 读取系统启动文件 /etc/systemd/system/default.target
#7. 读取系统初始化文件 /user/lib/sysetmd/system/sysinit.target
#8. 使服务器开机自启动 /etc/systemd/system 加载此目录中的信息，实现服务开机自动启动
#9. 运行mingetty进程，显示登陆界面
```

## 权限配置

```shell
#文件权限配置的结论
#1. root用户对所有文件有绝对的权限，只要有执行权限，root用户可以无敌存在
#2. 对于文件来说，写的权限和执行的权限，都需要有读权限配置
#3. 如果想对文件进行操作，必须对文件赋予读的权限
#4. 一个普通文件默认权限：644，保证属主用户对文件可以编辑，保证其他用户可以读取文件内容

#目录权限配置的结论
#1. root用户对目录信息有绝对权限
#2. 对于目录来说，写的权限和读的权限，都需要执行权限的配合
#3. 如果想对目录进行操作，必须对目录赋予执行权限
#4. 一个目录文件默认权限：755，保证属主用户对目录进行编辑，保证其他用户可以读取目录中的信息，并可以进入目录

chmod u+r/w/x
chmod u-r/w/x 
chmod u=rw
chmod 761
chmod a=x #所有用户添加可执行权限

#修改umask值可以修改默认目录文件权限，umask默认值0022
#默认文件权限：666-022=644
#umask值是奇数：666-033=633+11=644
#umask值是偶数：666-022=644
#默认目录权限：777-022=755
#umask值是奇数：777-033=744
#umask值是偶数：777-022=755
vim /etc/profile #永久修改umask信息

#设置特殊权限位
#rwx-w---x 9个权限位，实际有12个权限位
#setuid权限位设置，将文件属主拥有的能力，分配给所有人
chmod u+s /bin/cat
chmod 4755 /bin/cat
#setgid权限位设置，将文件属组拥有的能力，分配给所有用户组
#sticky bit粘滞位，可以将不同用户信息放置到共享目录中，实现不同用户数据可以互相查看，但是不可以互相随意修改
chmod o+t 目录信息
chmod 1777 目录信息

#防范系统中的重要文件不被修改
#1. 给文件加锁，使root用户也不可以修改
chattr +i /etc/passwd #设置方法
chattr -i /etc/passwd #解锁命令
mv /bin/chattr /root/charles #修改指令名称
```
## 用户相关文件和指令

```shell
useradd oldgirl #/home/oldgirl/目录中的数据内容会参考/etc/skel目录中的信息
.bash_history #历史命令记录文件，保存在磁盘中
history #历史命令保存在内存中
history #清空内存中历史命令
.viminfo #vim样式设置

/etc/passwd #记录系统用户信息文件
# 第一列，用户名
# 第二列，用户密码信息
# 第三列，uid信息
# 第四列，gid信息
# 第五列，注释信息
# 第六列，用户目录信息
# 第七列，用户登录系统方式
# 	/bin/bash，通用的解释器
# 	/usr/bin/sh，等价于/bin/bash
# 	/usr/bin/bash，等价于/bin/bash
# 	/sbin/nologin，无法登录系统
#	/usr/sbin/nologin，无法登录系统
/etc/shadow #系统用户密码文件
/etc/group #组用户记录文件
/etc/gshadow #组用户密码信息

useradd oldboy -M -s /sbin/nologin -u 2000 -g Alex -G Charles -c "manager database" #创建用户
# -M，不创建家目录
# -s，指定使用shell方式
# -u，指定用户uid数值信息
# -g，指定用户所属的主要组信息
# -G，指定用户所属的附属组信息
# -c，添加指定用户注释说明

usermod #修改用户信息
# -s，修改用户登录方式
# -g，修改用户的主要组信息
# -G，修改用户的附属组信息
# -c，修改用户的注释信息
# -u，修改用户uid数值信息

#删除用户信息
userdel -r #彻底删除用户以及用户的家目录

chown #修改属主和属组信息
chown oldboy.root /etc/hosts #修改文件属主和属组信息
chown -R Alex01.Alex01 oldboy_dir #递归修改目录&目录内文件的属主和属组信息

id #显示用户信息
w #显示正在登录系统的用户信息
# USER，什么用户登录系统
# TTY，登录方式
# pts/x，远程登录
# tty1，本地登录
# echo "message" > /dev/pts/1，发送信息给pts/1用户
# FROM，从哪里登录服务器
# LOGIN，登录时间
# IDLE，空闲时间
# JCPU PCPU，用户操作系统消耗的CPU资源时间
# WHAT，用户在干什么

last #最近谁登录系统
lastlog #显示所有用户最近一次远程登录的信息

#用户权限赋予
# 1. 直接切换root账号，su -root
# 2. 给文件赋予权限
# 3. root赋予普通用户权限
visudo #93行添加，oldboy ALL=(ALL) /usr/sbin/useradd, /user/bin/rm
sudo -l #验证已获得的权限
sudo useradd Alex21

su root #部分环境变量切换有变化
su - root #全部环境变量切换有变化

#sudo功能配置说明
#1. 给更多权限
oldboy ALL=(ALL) /user/sbin/*, !/user/sbin/visudo, /usr/bin/*
#2. 不需要账号密码
oldboy ALL=(ALL) NOPASSWD: /user/sbin/*, !/user/sbin/visudo, /usr/bin/*
```

## 定时服务

```shell
#定时任务实现方式
#日志文件需要定期进行切割处理

#系统特殊目录，将脚本放到对应目录后自动执行：
/etc/cron.hourly
/etc/corn.daily
/etc/corn.weekly
/etc/corn.monthly

#用户定时任务
crontab -l #查看
crontab -e #编辑
vim /var/spool/cron/root #root用户设置的定时任务配置文件
vim /var/spool/cron/oldboy #oldboy用户设置的定时任务配置文件

cat /etc/crontab #查看规则
00 02 * * * #每天2点
*/5 * * * * #每5分钟
01-05 02 * * * #2:01, 2:02, 2:03, 2:04, 2:05
00 14,20 * * * #每天14和20点
20/10 01 * * * #1点20开始每隔10分钟执行一次

#定时任务排查方法
cat /var/spool/cron/root #检查文件
cat /car/log/cron #检查日志

# 规范：
# 1. 需要有注释
# 2. 尽量使用绝对路径
# 3. 命令需要使用绝对路径（定时任务执行时，识别的PATH信息只有/usr/bin:/bin）
# 4. 编写定时任务时，可以将输出到屏幕上的信息保存到黑洞里，避免占用磁盘空间
* * * * * sh test.sh &>/dev/null
# 5. 编写定时任务，尽量不要产生屏幕输出信息
# 6. 多个定时任务命令，最好使用脚本实现
# 7. 定时任务中无法识别任务中的一些特殊符号
* * * * * /bin/date "+\%F \%T" > /tmp/time.txt，使用转义字符
# 利用脚本编写任务

# 补充：
# 定时任务输出到屏幕上的信息都会以邮件的方式告知用户，mail放在如下目录/var/spool/mail/root，若关闭systemctl stop postfix，则会在如下目录中生成很多草稿/var/spool/postfix/maildrop/*
```

## 磁盘管理

```shell
#分区
#1. 插入新硬盘10G
#2. 检查是否识别到新磁盘 
ll /dev/sdb
#3. 对磁盘进行分区处理
fdisk -l #查看分区信息
fdisk /dev/sdb #对磁盘进行分区
d #删除分区*****
g #创建新的GPT分区表
l #列出可以分区的类型
m #输出帮助菜单
n #新建一个分区*****
p #输出分区结果信息*****
q #不保存退出
t #改变分区的系统id==改变分区类型
u #改变分区方式，是否按照扇区划分
w #保存退出，将分区的信息写入分区表*****
#4. 让系统可以加载识别分区信息
partprobe /dev/sdb

#格式化
mkfs.xfs /dev/sdb1
mkfs -t xfs /dev/sdb2
ext3/4 #centos6
xfs #centos7 格式化效率较高，数据存储效率提升（数据库服务器）

#挂载应用
mount /dev/sdb1 /mnt
df -h #检查是否挂载ok

#自动挂载
vim /etc/rc.local #放入开机启动
vim /etc/fstab #修改磁盘挂载文件
#uuid，挂载点，指定文件系统格式，defaults挂载参数，0不备份磁盘，0不检查磁盘
blkid #获取UUID

# 分区大于2TB的硬盘
# 1. 使用parted命令进行分区
# 2. 使用parted命令进行分区
mklabel gpt #创建一个分区表，gpt可以创建多余4个的主分区
print #显示分区信息
mkpart #创建一个分区
quit #退出分区状况
# 3. 加载磁盘分区
partprobe /dev/sdc
# 4. 格式化
mkfs.xfs /dev/sdc1
# 5. 挂载

# 企业磁盘常见问题
# 1. 删除没用的数据
# 2. 找出大的没用数据
find / -type f -size +xxx
du -sh /* | sort -h
# 3. inodes用完
df -i

# 如何调整swap空间
dd if=/dev/zero of=/tmp/1G bs=100M count=10 #创建1G大小文件
mkswap /tmp/1G #指定空间作为swap空间
swapon /tmp/1G #加载使用swap空间
```


## 其他知识

```shell
rpm -ivh XXX.rpm #手动安装软件

#linux和windows主机之间传输数据
yum install -y lrzsz
#在linux上进行操作
rz -y #从windows上下载重要数据信息
sz -y #数据信息，从linux上上传重要数据到windows

dd if=/dev/zero of=/tmp/oldboy.txt bs=10M count=100 #创建1G大小文件

sort -n -k2 #按照数字，按照第二列进行排序
```