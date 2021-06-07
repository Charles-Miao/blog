---
title: "Linux基础 - Part4"
date: 2021-06-05T21:55:22+08:00
description: ""
draft: false
tags: [Linux]
categories: [运维]
---

# 主要内容

- 交换机和路由器
- 网络层次模型
- TCP三次握手和四次挥手
- 相关网络协议
- 子网和路由
- 网络服务
- 其他知识

<!--more-->

## 交换机和路由器
```shell
# 交换机（广播），路由器（路由表）

# 路由表信息如何生成
# 1. 直连网络环境自动生成
# 2. 利用手工配置，静态配置
# 3. 利用路由协议自动生成，动态配置

# 动态路由配置
# RIP动态路由配置，把自动生成的发布出去

# 网络架构设计方法：
# 核心层：路由器，网关接口，实现和外网通讯，需要有冗余能力
# 汇聚层：交换机，三层交换机，需要有冗余能力，策略控制
# 接入层：交换机，二层交换机，终端设备接入网络
```

![switch_router](https://github.com/Charles-Miao/blog/blob/master/static/Network/%E4%BA%A4%E6%8D%A2%E6%9C%BA&%E8%B7%AF%E7%94%B1%E5%99%A8.GIF?raw=true)

## 网络层次模型

### OSI7层模型
```shell
# 应用层，应用程序接口规范
# 表示层，数据转换加密压缩
# 会话层，控制网络连接建立或者终止
# 传输层，保证数据传输的可靠性
# 网络层，可以实现透过路由找到目标网络，路由能力，三层设备
# 数据链路层，可以实现透过交换找到真正目标主机，交换能力，二层设备
# 物理层，指定一些网络物理设备标准，网卡，网线，光纤
```

### OSI7层模型建立主机与主机之间的通讯(封装和解封装)

![Encapsulation](https://github.com/Charles-Miao/blog/blob/master/static/Network/OSI%E6%95%B0%E6%8D%AE%E5%B0%81%E5%8C%85%E8%A3%85%E8%BF%87%E7%A8%8B.JPG?raw=true)
![Decapsulation](https://github.com/Charles-Miao/blog/blob/master/static/Network/OSI%E4%BA%92%E8%81%94%E6%95%B0%E6%8D%AE%E5%8C%85%E8%A7%A3%E5%B0%81%E8%A3%85%E8%BF%87%E7%A8%8B.JPG?raw=true)
![Encap_Decap](https://github.com/Charles-Miao/blog/blob/master/static/Network/%E6%95%B0%E6%8D%AE%E5%B0%81%E8%A3%85%E4%B8%8E%E8%A7%A3%E5%B0%81%E8%A3%85%E8%BF%87%E7%A8%8B.JPG?raw=true)


### TCP/IP四层模型

```shell
# TCP协议：传输控制协议，面向连接的网络协议，在线发送文件，数据传输可靠性高，传输效率低
# UDP协议：用户报文协议，无连接的网络协议，离线发送文件，数据传输可靠性低，传输效率高
```
![protocol](https://github.com/Charles-Miao/blog/blob/master/static/Network/TCP%20IP%E7%9B%B8%E5%85%B3%E5%8D%8F%E8%AE%AE.JPG?raw=true)
 
![OSI7_TCP_IP](https://github.com/Charles-Miao/blog/blob/master/static/Network/OSI%E6%A8%A1%E5%9E%8B%E5%92%8CTCP%20IP%E6%A8%A1%E5%9E%8B%E5%AF%B9%E5%BA%94%E5%85%B3%E7%B3%BB.JPG?raw=true)

## TCP三次握手和四次挥手

```shell
# 预备知识：
# 源端口，目标端口
# 端口号最多为65535，2的16次方
# 控制字段
# syn(1)，请求建立连接控制字段
# fin(1)，请求断开连接控制字段
# ack(1)，数据信息确认控制字段
```

### TCP三次握手

```shell
# 1. 主机A向主机B发送TCP报文，报文中控制字段syn置为1，请求建立连接
# 2. 主机B向主机A发送TCP响应报文，报文中控制字段syn置为1，ack置为1
# 3. 主机A向主机B发送TCP报文，报文中控制字段ack置为1，确认主机B发送信息已经接收到了

# 1. 发送syn请求建立连接控制字段，发送seq序列号信息（X），第一个数据包的序列号默认为0
# 2. 发送syn请求建立连接控制字段，同时还会发送ack确认控制字段
#     发送seq序列号信息（Y），还会发送ACK确认号（X+1）信息（对上一个数据序列号信息进行确认）
# 3. 发送ack确认控制字段，发送seq序列号信息（X+1），发送ack确认号（Y+1）
```

![three_handshake](https://github.com/Charles-Miao/blog/blob/master/static/Network/%E4%B8%89%E6%AC%A1%E6%8F%A1%E6%89%8B%E7%AE%80%E5%9B%BE.JPG?raw=true)

![three_handshake](https://github.com/Charles-Miao/blog/blob/master/static/Network/%E6%95%B0%E6%8D%AE%E5%B0%81%E8%A3%85%E4%B8%8E%E8%A7%A3%E5%B0%81%E8%A3%85%E8%BF%87%E7%A8%8B.JPG?raw=true)

### TCP四次挥手
```shell
# 1. 发送find请求断开连接控制字段
# 2. 发送ack确认控制字段
# 3. 发送find请求断开连接字段，发送ack确认字段
# 4. 发送ack控制字段
```

![four_wave](https://github.com/Charles-Miao/blog/blob/master/static/Network/%E5%9B%9B%E6%AC%A1%E6%8C%A5%E6%89%8B.JPG?raw=true)

### TCP的十一种状态集
```shell
# TCP三次握手：5种状态
# 0. 最开始2台主机都处于关闭状态	closed
# 1. 服务端将相应服务进行开启		closed --- listen
# 2. 客户端向服务端发出连接请求		closed --- syn_sent
# 3. 服务端接收到连接请求，进行去确认	listen --- syn_rcvd
# 4. 客户端再次进行确认		syn_sent --- established
# 5. 服务器接收到确认信息		syn_rcvd --- established

# TCP四次握手
# 1. 客户端发送请求断开连接信息			established --- fin_wait1
# 2. 服务器接收断开连接请求，并进行确认		established ---close_wait
# 3. 客户端接收到了确认信息			fin_wait1 --- fin_wait2
# 4. 服务端发送ack和fin字段			close_wait --- last_ack
# 5. 客户端接收到请求断开连接信息，发送确认	fin_wait2 --- time wait
# 6. 服务器端接收到确认信息			last_ack --- closed
# 7. 客户端等待一段时间			time_wait --- closed
```
![three_handshake](https://github.com/Charles-Miao/blog/blob/master/static/Network/%E4%B8%89%E6%AC%A1%E6%8F%A1%E6%89%8B%E7%8A%B6%E6%80%81%E5%8F%98%E5%8C%96%E9%9B%86.JPG?raw=true)

![four_wave](https://github.com/Charles-Miao/blog/blob/master/static/Network/%E5%9B%9B%E6%AC%A1%E6%8C%A5%E6%89%8B%E7%8A%B6%E6%80%81%E5%8F%98%E5%8C%96%E9%9B%86.JPG?raw=true)

## 相关网络协议

### DNS解析原理

```shell
yum install -y bind-utils
dig www.baidu.com #查看运行解析信息
dig www.baidu.com +trace #追踪解析过程
```

![dns1](https://github.com/Charles-Miao/blog/blob/master/static/Network/DNS1.JPG?raw=true)
![dns2](https://github.com/Charles-Miao/blog/blob/master/static/Network/DNS2.JPG?raw=true)
![dns3](https://github.com/Charles-Miao/blog/blob/master/static/Network/DNS3.JPG?raw=true)


### ARP协议

```shell
# ARP，已知IP地址解析mac地址信息
# 方法：在知道ip地址，不知道mac地址的情况下，发送一个广播到对应主机即可知道mac地址
# 作用：减少交换网络中广播的产生
```
![arp](https://github.com/Charles-Miao/blog/blob/master/static/Network/ARP.JPG?raw=true)

## 子网和路由

```shell
#私网地址网段不能出现在公网路由器路由表中
#不划分子网，会造成地址浪费，广播风暴，路有压力
```
### 系统静态路由配置
```shell
# centos6，route，和网络相关的命令使用net-tools
rpm -qf `which route`
# 静态默认路由：
# 1. 编写网卡配置文件
# 2. 利用命令临时配置
route add default gw 10.0.0.254
route del default gw 10.0.0.254
# 静态网段路由：
route add  net 172.16.1.0 netmask 255.255.255.0 gw 192.168.1.1
route del  net 172.16.1.0 netmask 255.255.255.0 gw 192.168.1.1
# 静态主机路由：
route add -host 10.0.3.201 dev eth1
route del -host 10.0.3.201 dev eth1
```
```shell
# centos7，ip route，和网络相关的命令使用iproute
rpm -qf `which ip`
# 静态默认路由：
# 1. 编写网卡配置文件
# 2. 利用命令临时配置
ip route add default via 10.0.0.2
ip route del default via 10.0.0.2
# 静态网段路由：
ip route add  net 172.16.1.0 netmask 255.255.255.0 via 192.168.1.1
ip route del  net 172.16.1.0 netmask 255.255.255.0 via 192.168.1.1
# 静态主机路由：
ip route add -host 10.0.3.201 via 10.0.1.2
ip route del -host 10.0.3.201 via 10.0.1.2
```

## 网络服务

```shell
nslookup #域名解析命令
traceroute #路由跟踪命令
```

### SSH服务

```shell
#scp远程复制
scp root@192.168.44.2:/root/test.txt . #下载
scp -r /root/123/ root@192.168.44.2/root #上传

#sftp文件传输和登录
sftp root@192.168.4.2
ls #查看服务器
cd #切换服务器目录
lls #查看本地数据
lcd #切换本地目录
get #下载
put #上传

#密钥对验证
ssh-keygen -t rsa #step1:client端生成秘钥
#step2:把公钥传到服务器端
cat id_rsa.pub >> /root/.ssh/authorized_keys #step3:将公钥上传到服务器端
chmod 600 authorized_keys #step4修改文件权限
```

### DHCP服务
![dhcp](https://github.com/Charles-Miao/blog/blob/master/static/Network/DHCP.JPG?raw=true)

```shell
# 端口号
# ipv4 udp67，udp68
# ipv6 udp546，udp547

#配置dhcp服务器
vi /etc/dhcp/dhcpd.conf
service dhcpd restart

#配置客户端
vim /etc/sysconfig/network-scripts/ifcfg-eth0
service network restart

#服务器端查看分配的地址
vim /var/lib/dhcpd/dhcpd.leases
#客户端查看分配的地址
vim /var/lib/dhclient/dhclient-eth0.leases
```

### vsftp服务

```shell
# 主动模式和被动模式
# 主动模式端口为20，被动模式是随机端口
# 主动模式（默认模式），client端防火墙可能会屏蔽20端口，client可能无法访问ftp服务
# 被动模式，client端主动访问服务器，服务器端口可控，防火墙设定可控，不存在访问不了的问题

vim /etc/vsftpd/vsftpd.conf #配置文件

#用户控制列表文件
/etc/vsftpd/ftpusers
/etc/vsftpd/user_list

# 匿名访问注意事项
# 1. 默认上传目录：/var/ftp/pub/
# 2. 如果允许上传，需要服务权限和系统目录权限同时允许
# 3. vsftp服务的伪用户是ftp

# 本地用户访问
# 1. 本地用户账号，如果允许上传，需要服务权限和系统目录权限同时允许
# 2. chroot_local_user=YES，开启用户目录限制，把用户限制在用户主目录中
# 3. chroot_list_enable=YES
# chroot_list_file=/etc/vsftpd/chroot_list，此文件中的用户可以随便切换目录

# 虚拟用户访问
# 1. 添加虚拟用户口令文件
# 2. 生成虚拟用户口令认证文件（yum -y install db4-utils，db_load指令将文本转变成认证数据库）
# 3. 编辑vsftpd的PAM认证文件，vi /etc/pam.d/vsftpd
# 4. 建立本地映射用户并设置宿主目录权限
# useradd -d /home/vftproot -s /sbin/nologin vuser
# chmod 755 /home/vftproot
# 5. 修改配置文件
# guest_enable=YES
# guest_username=vuser
# pam_service_name=vsftpd
# 6. 重启vsftpd服务，并测试
# 7. 调整虚拟用户权限
# anonymous_enable=NO
# anon_upload_enable=YES
# anon_mkdir_write_enable=YES
# anon_other_write_enable=YES

# 为每个虚拟用户配置不同的权限
# 1. 修改配置文件
# user_config_dir=/etc/vsftpd/vusers_dir
# 2. 为每个虚拟用户建立配置文件
# vim /etc/vsftpd/vusers_dir/cangls
# anon_upload_enable=YES
# anon_mkdir_write_enable=YES
# anon_other_write_enable=YES
# local_root=/tmp/vcangls
```

### samba服务

```shell
#samba安装
service smb start
service nmb start

#相关文件
/etc/samba/smb.conf
/etc/samba/lmhosts
/etc/samba/smbpasswd
/etc/samba/smbusers #用户别名，用于适应不同操作系统中用户名习惯
testparm #监测配置文件是否正确

# share级别：
# chown nobody /study/，share方式共享目录时，需要将目录改为所有用户可以访问
# 创建的共享目录需要修改所有者，否则无法正常访问（系统权限和配置文件里的权限都需要允许）

#linux客户端访问
smbclient -L //192.168.123.210 #查看主机共享资源
smbclient //192.168.123.210/share #访问共享目录，指令类似ftp

#user级别：
smbpasswd -a username #为系统用户单独设定samba密码
#ftp建议使用虚拟用户，从安全性考虑，虚拟用户不可以登录系统
pdbedit -a -u username #同smbpasswd命令
pdbedit -L #查看已经存在samba用户
pdbedit -x -u username #删除samba用户
smbpasswd -x username #删除samba用户

# 多用户，多用户，多权限设定
# 1. 先设定文件夹，和samba配置档案（可查看，可写），不设定特定用户权限
# 2. 再设定文件夹权限700，chomd 700 share_folder
# 3. 创建samba密码，smbpasswd -a username
# 4. 使用acl指令设定特定用户权限，setfacl -m u:username:rwx share_folder/
# 5. 查询权限设定结果，getfacl share_folder/

mount -t cifs -o username=username //ip/share_folder /local_folder #挂载到本地使用
```

## 其他知识

```shell
netstat -an | grep ESTABLISHED #查看client端连接数
```