---
title: "Linux基础 - Part1"
date: 2021-05-23T21:39:49+08:00
description: ""
draft: false
tags: [Linux]
categories: [运维]
---

- 硬件系统
- 系统管理命令
- 快捷键
- 系统目录结构
- 重要文件
- vim快捷键
- 系统优化
- 其他指令

<!--more-->

硬件系统
---
- 内存中两个存储空间
- 高并发和低并发发数据存储
- 磁盘接口类型
- 多块硬盘整合优势
- 远程管理卡
- dell，联想，浪潮，华为

系统管理命令
---

```shell
shutdown -h
shutdown -r
shutdown -c

ls
ls -d
ll == ls -l

mkdir -p
cd
pwd

man

touch
vim
cat

cp -r
\cp
rm -rf
\rm
mv
```

快捷键
---

```shell
# ctrl+l,清屏指令
# ctrl+d,注销
# ctrl+a,行首
# ctrl+e,行尾
# ctrl+左右方向键,单个词组移动
# ctrl+w,字符剪切
# ctrl+u,行首到光标剪切
# ctrl+k,光标到行尾剪切
# ctrl+y,黏贴
# esc+.,上一行指令的最后一个参数
```

系统目录结构
---

```shell
# bin, sbin
# boot
# dev
# etc
# home, root
# lib, lib64
# lost+found
# mnt
# opt
# proc
# /etc/selinux
# sys
# tmp
# usr
# var
```

重要文件
---

```shell
#网卡配置
vim /etc/sysconfig/network-scripts/ifcfg-eth0
systemctl restart network

#DNS解析配置
vim /etc/sysconfig/network-scripts/ifcfg-eth0

#主机名
vim /etc/hostname
hostnamectl set-hostname newname

#解析映射文件
vim /etc/hosts

#磁盘挂载文件（df，查看磁盘挂载状况）
vim /etc/fstab

#开机自启动
vim /etc/rc.local

#cetnos6系统运行级别(0/1/2/3/4/5/6)
vim /etc/inittab

#centos7系统运行级别(poweroff.target/ rescue.target/ multi-user.target/ graphical.target/ reboot.target)
systemctl get-default
systemctl set-default rescue.target
ls –l /usr/lib/system/system/runlevel*target

#变量加载文件
vim /etc/profile==/etc/bashrc
vim ~/.bashrc==~/.bash_profile
source /etc/profile
which
export

#系统别名
alias

#登陆之后提示信息
vim /etc/motd

#登陆之前提示信息
vim /etc/issue

#硬件信息
cat /proc/cpuinfo
cat /proc/loadavg
w
cat /proc/meminfo
free –h
cat /proc/mounts
df –h

#系统版本
cat /etc/redhat-release
uname –a

#优化命令提示符颜色
vim /etc/profile
export PS1='\[\e[32;1m\][\u@\h \W]\$ \[\e[0m\]'
source /etc/profile
```

vi快捷键
---
```shell
I #将光标移至行首，再进入编辑状态
o #在光标所在行下面，新起一行进行编辑（重点）
O #在光标所在行上面，新起一行进行编辑
a #将光标移动到右边下一个字符，进行编辑
A #将光标移动到行尾，并进行编辑（重点）
C #将光标到行尾进行剪切，并进入编辑（重点）
cc #将整行进行删除，并进入编辑

G #将光标移至尾部
gg #将光标移至首部
ngg #n表示移到第几行
$ #将光标移至一行的结尾
0或^ #移到一行的行首

/ #底行模式搜索，向下搜索
? #底行模式搜索，向上搜索

p #将内容进行粘贴
np #多行粘贴
yy #复制
nyy #多行复制

dd, u #删除和恢复

#查看文件时显示行号和不显示行号
:set nu
:set nonu

ctrl+r #redo和undo相反
dG #将光标位置删除到文章底部

:set ic #忽略大小写查找
:set noic #不忽略大小查找
/search-text\c #忽略大小写查找

#vim高级功能
/#搜索文件中没有的信息，取消高亮
:2,4move9 #将第2行~4行的内容移到第9行
:2,4copy9 #将第2行~4行的内容拷贝到第9行
:%s#oldboy #oldgirl#g#将文件中指定内容全部替换
#s substitute 替换
#g global 全局
:2,4s#oldboy#oldgirl#g #替换部分内容第2~4行
:12,$s#oldboy#oldgirl#g #替换部分内容第12行~结尾

#批量添加信息
ctrl+v #进入视图模式
#方向键选择
shift+i #进行单行编辑
esc #实现批量修改

#批量删除信息
ctrl+v #进入视图模式
#方向键选择
d or x #删除
```

系统优化
---

```shell
#	yum源优化
#	防火墙优化
#	selinux优化，vim /etc/selinux/config
#	字符编码优化，vim /etc/locale.conf
#	优化远程连接速度，vim /etc/ssh/sshd_config，vim /etc/hosts
```

其他指令
---

```shell
tail -6
head -5
tail –f

#创建用户
useradd charles
passwd charles

#rpm指令
rpm -qa sl #query查询软件安装版本
rpm -ql sl #查询并list出所有安装的数据
rpm -qf ssh #查看命令属于哪个软件包
rpm -qf `which ssh`

#ss==netstat（yum install -y net-tools）
ss -lntup
#-l list
#-n number
#-t tcp协议
#-u udp协议
#-p process进程信息

#按照时间排序
ls -ltr /etc/
#t，按时间排序
#r，逆向排序

cat -n /oldboy/oldboy.txt #查看文件，并显示行号

less /etc/service #查看文件
#回车，向下逐行
#空格，向下逐页
#方向键上，向上逐行
#b，向上逐页

#多行添加文件
cat >> /oldboy/oldboy.txt <<EOF
> oldboy01
> oldboy02
> oldboy03
> EOF

```



