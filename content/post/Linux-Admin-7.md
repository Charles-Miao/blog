---
title: "Linux基础 - Part7"
date: 2021-06-23T22:59:59+08:00
description: ""
draft: false
tags: [Linux]
categories: [运维]
---

# 主要内容

- nginx服务部署安装
- nginx目录结构
- nginx服务的企业应用
- nginx访问模块
- 网站的LNMP架构部署
- 负载均衡
- 高可用服务

<!--more-->

> [详细笔记](https://github.com/Charles-Miao/Linux/blob/master/Linux%E5%9F%BA%E7%A1%80/%E7%AC%94%E8%AE%B037~43.txt)

## nginx服务部署安装

### 编译安装
```shell
wget http://nginx.org/download/nginx-1.16.0.tar.gz #1
# 2. 解压软件
# 3. 配置操作
./confgure --prefix= --user=USER
# --prefix=PATH，指定安装路径
# --user=USER，设置一个虚拟用户管理worker进程（安全）
# --group=GROUP，设置一个虚拟用户组管理worker进程（安全）
# 4. 进行软件的编译
make
# 5. 编译安装过程
make install
```
### yum官方源安装方式
```shell
vim /etc/yum.repos.d/nginx.repo #1
[nginx-stable]
name=nginx stable repo
baseurl=http://nginx.org/packages/centos/$releasever/$basearch/
gpgcheck=1
enabled=1
gpgkey=https://nginx.org/keys/nginx_signing.key
# 2. yum安装nginx软件
yum install -y nginx
# 3. 启动nginx
systemctl start nginx
systemctl enable nginx
```

## nginx目录结构

### /etc/logrotate.d
```shell
# 1. /etc/logrotate.d，实现nginx日志文件定时切割处理
# 1.1 利用脚本切割
mv /var/log/nginx/access.log /var/log/nginx/access_$(date +%F).log
systemctl restart nginx
# 1.2 利用转悠文件切割程序--logrotate
vim /etc/logrotate.conf
# weekly，定义默认日志切割周期
# rotate 4，定义只保留几个切割后的文件
# create，创建出一个相同的源文件
# dateext，定义角标（扩展名信息）
# compress，是否对切割后的文件进行压缩处理
# include /etc/logrotate.d，加载此目录文件配置文件

cat /etc/logrotated.d/nginx
/var/log/nginx/*.log{
daily
missingok
rotate 52
compress
delaycompress
notifempty
create 640 nginx adm
sharedscripts
postotate
	if [ -f /var/run/nginx.pid ]; then
		kill -USR1 `cat /var/run/nginx.pid`
	fi
endscript
}
```

### /etc/nginx，配置文件
### /var/log/nginx，日志文件
### /usr/bin/nginx，命令文件
### /usr/share/nginx/html，站点目录

### /etc/nginx/nginx.conf，nginx服务配置文件
```shell
/etc/nginx/nginx.conf #主配置文件
# 第一个部分：配置文件主区域配置
user www;	定义worker进程管理的用户
补充说明：
master process	主进程，管理服务是否能够正常运行，boss
worker process	工作进程，处理用户的访问请求，员工
worker_processes 2;	定义有几个worker进程，CPU核数/ 核数的2倍
error_log /var/log/nginx/error.log warn;	定义错误日志路径信息
pid /var/run/nginx.pid;	定义pid文件路径信息
#第二个部分：配置文件事件区域
events {
	worker_connections 1024;	一个worker进程可以同时接受1024访问请求
}
#第三个部分：配置http区域
http {
	include	/etc/nginx/mime.types;	加载一个配置文件
	default_type	application/octet-stream;	指定默认识别文件类型
	log_format	oldboy	'$remote_addr - $remote_user [$time_local] "$request"'
				'$status $body_bytes_sent "$http_referer"'
				'"http_user_agent" "$http_x_forwarded_for"';	定义日志格式
	access_log	/var/log/nginx/access.log	oldboy;	指定日志路径
	sendfile		on;	？？？
	#tcp_nopush	on;	？？？
	keepalive_timeout	65;	超时时间
	#gzip	on;
	include /etc/nginx/conf.d/*.conf;	加载一个配置文件
}

/etc/nginx/nginx.d/default，扩展配置（虚拟主机配置文件）
#第四个部分：server区域信息（配置一个网站www、bbs、blog==一个虚拟主机）
server {
	listen	80;			指定监听的端口
	server_name	localhost;		指定网站域名
	location / {
		root /user/share/nginx/htm;	定义站点目录位置
		index index.html index.htm;	定义首页文件
	}
	error_page 500 502 503 504 /50x.html;
	location=/50x.html {
		root /usr/share/nginx/html;
	}
}
```

## nginx服务的企业应用
### 利用nginx服务搭建一个网站
```shell
# 1. 利用nginx服务搭建一个网站
# 1.1编写虚拟主机配置文件
vim www.conf
server {
	listen	80;
	server_name	www.oldboy.com;
	location	/oldboy {
		root /user/share/nginx/html;
		index oldboy.html;
	}
}
# 1.2需要获取开发人员编写的网站代码
# 1.3重启nginx服务
# 两种方法：
systemctl reload nginx
nginx -s reload
# nginx命令参数
# -t，检查测试配置文件语法
# -s，控制服务停止或者重新启动
# 1.4编写DNS信息
# 真实域名：在阿里云上进行DNS解析记录配置
# 模拟域名：在windows主机的hosts文件中进行配置即可
c:\windows\system32\drivers\etc\hosts
# 1.5进行测试访问
http://www.oldboy.com

# 部署搭建网站常见错误：
# 1. 网站服务配置文件编写不正确
# 404错误
# 方法一：修改nginx配置文件---location
# 方法二：在站点目录中创建相应目录或文件数据信息
# 403错误
# 方法一：不要禁止访问
# 方法二：因为没有首页文件
# 2. DNS信息配置不正确
# 3. nginx配置文件修改一定要重启服务
# 站点目录中代码文件信息调整，不需要重启服务
```

### 利用nginx服务搭建一个多网站（www bbs blog）
```shell
# 1. 创建多个虚拟主机配置文件
bbs.conf
server {
	listen	80;
	server_name	bbs.oldboy.com;
	location	/	{
	root	/html/bbs;
	index	index.html;
	}
}
blog.conf
server {
	listen	80;
	server_name	blog.oldboy.com;
	location	/	{
	root	/html/blog;
	index	index.html;
	}
}
www.conf
server {
	listen	80;
	server_name	www.oldboy.com;
	location	/	{
	root	/html/www;
	index	index.html;
	}
}
# 2. 创建站点目录和目录中首页文件
mkdir /html/{www,bbs,blog} -p
for name in {www,bbs,blog}; do echo "10.0.0.7 $name.oldboy.com" > /html/$name/index.html; done
for name in {www,bbs,blog}; do cat /html/$name/index.html; done
# 3. 编写hosts解析文件
10.0.0.7	www.oldboy.com bbs.oldboy.com blog.oldboy.com
# 4. 进行访问测试
# 4.1 利用windows进行浏览器访问测试
# 4.2 利用linux进行命令访问测试，curl www.oldboy.com
```
### 企业中虚拟主机访问方式
```shell
# 1. 基于域名的方式进行访问
# 2. 基于地址的方式进行访问：只能指定地址访问 --- 负载均衡+高可用服务
server {
	listen	10.0.0.7:80;
	server_name	www.oldboy.com;
	location	/	{
	root	/html/www;
	index	index.html;
	}
}
# ps:服务配置文件中设计到地址修改，必须重启nginx服务，不能平滑重启
# 3. 基于端口的方式进行访问：zabbix服务（apache：80）+web服务（nginx：80）
server {
	listen	8080;
	server_name	www.oldboy.com;
	location	/	{
	root	/html/www;
	index	index.html;
	}
}
```

### 网站页面访问原理：
```shell
# 1. 将域名进行解析 www.oldboy.com --- 10.0.0.7
# 2. 建立tcp的连接（四层协议）
#     10.0.0.7 目标端口 80
# 3. 根据应用层http协议发出请求
#     请求报文：hosts：bbs.oldboy.com
# 4. 没有相同域名的server主机，会找满足端口要求的第一个主机
#     显示主机的网站页面
```

## nginx访问模块

### nginx访问模块：ngx_http_access_module
```shell
# 企业中网站的安全访问配置
# 1. 根据用户访问的地址进行控制
# 10.0.0.0/24 www.oldboy.com/AV/ 不能访问
# 172.16.1.0/24 www.oldboy.com/AV/ 可以访问
```
```shell
# 举例配置：
location / {
	deny	192.168.1.1;
	allow	192.168.1.0/24;
	allow	10.1.1.0/16;
	allow	2001:0db8::/32;
	deny	all;
}

# 1.1 编写配置文件
vim www.conf
server {
	listen	80;
	server_name	www.oldboy.com;
	location	/	{
	root	/html/www;
	index	index.html;
	}
	location	/AV	{
	deny	10.0.0.0/24;
	allow	172.16.1.0/24;
	root	/html/www;
	index	index.html;
	}
}
# 补充：
# location外面的信息，全局配置信息
# location里面的信息，局部配置信息
```

### nginx认证模块：ngx_http_auth_basic_module
```shell
# 2. 根据用户访问进行认证
# 举例配置：
location / {
	auth_basic	"closed site";	开启认证功能
	auth_basic_user_file	conf/htpasswd;	加载用户密码文
}
# 2.1 编写虚拟主机配置文件
server	{
	listen	80;
	server_name	www.oldboy.com;
	location	/	{
		root	/html/www;
		index	index.html;
		auth_basic	"oldboy-sz-01";
		auth_basic_user_file	password/htpasswd;
	}
}
# 2.2 创建密码文件
# htpasswd参数说明：
# -c，创建一个密码文件
# -n，显示文件内容
# -b，免交互方式输入用户密码信息
# -m，md5加密算法
# -B，使用bcrypt对密码进行加密
# -C，使用bcrypt algorithm对密码进行加密
# -d，密码加密方式
# -s，加密方式
# -p，不进行加密
# -D，删除指定用户

# 修改密码文件权限
# chmod 600 ./htpasswd
# chown www htpasswd

# 500 Internal Server Error
# 1. 内部程序代码编写有问题
# 2. 程序服务中文件权限不正确

curl www.oldboy.com -u oldboy:123456
```
### nginx模块功能：ngx_http_autoindex_module
```shell
# 1. 利用 nginx服务搭建网站文件共享服务器
# 第一个步骤：编写配置文件（www.conf）
server	{
	listen	80;
	server_name	www.oldboy.com;
	location	/	{
		root	/html/www;
		auth_basic	"oldboy-sz-01";
		auth_basic_user_file	password/htpasswd;
		autoindex	on;	开启nginx站点目录索引功能（类似mirror.aliyun.com）
	}
}
# PS:	1. 需要将首页文件进行删除
# 	2. mine.types媒体资源类型文件作用
# 		文件中有的扩展名信息资源，进行访问时会直接看到数据信息
# 		文件中没有的扩展名信息资源，进行访问时会直接下载资源

# 网站页面目录数据，中文出现乱码，如何解决
location	/	{
	root	/html/www;
	...
	charset	utf-8;	修改目录结构中出现的中文乱码问题
}

# 2. 利用nginx服务搭配置文件别名功能
# 2.1 编写配置文件
server_name	www.oldboy.com old.com;
# 2.2 配置好解析信息（local测试：修改本地的host文件）

# 作用：
# a. 编写网站访问测试
# b. 定位要访问的网站服务器（集群多台服务器时，可以用于定位特定服务器）
```
### 状态模块：ngx_http_stub_status_module
```shell
# 3. 利用nginx状态模块功能对网站进行监控
# 3.1 编写配置文件
vim state.conf
server	{
	listen	80;
	server_name	state.oldboy.com
	stub_status;
}
# 3.2 重启nginx服务，并且编写解析文件
systemctl reload nginx
10.0.0.7	state.oldboy.com

# Active connections：激活的连接数信息
# accepts：接收的连接数汇总 TCP
# handled：处理的连接数汇总 TCP
# requests：总计的请求数量 HTTP协议请求
# Reading：nginx服务读取请求报文数量	100人点餐
# Writing：nginx服务响应报文信息数量	100人响应
# Waiting：nginx队列机制，要处理（读取或响应保存进行保存）	监控
```
### ngx_http_log_module
```shell
# 4. nginx日志功能配置
# 访问日志：/var/log/nginx/access.log	ngx_http_log_module
log_format	main	'$remote_addr - $remote_user [$time_local] "$request"'
			'$status $body_bytes_sent "$http_referer"'
			'"$http_user_agent" "$http_x_forwarded_for"';	定义日志格式
access_log	/var/log/nginx/access.log	main;			调用日志格式
$remote_addr		显示用户访问源IP地址信息
$remote_user		显示认证用户名信息
[$time_local]		显示访问网站时间
$request			请求报文的请求信息
$status			状态码信息
$body_bytes_sent		响应数据尺寸信息
$http_referer		记录调用网站资源的连接地址信息（推广&防止用户盗链）
$http_user_agent		记录用户使用什么客户端软件进行访问页面的（chrome，firefox，IE，Android，IOS）
$http_x_forwarded_for	？？？负载均衡

# 错误日志：/var/log/nginx/error.log	Core functionality
# error_log	/var/log/nginx/error.log warn;	指定错误日志路径以及错误日志记录的级别
# 错误级别：
# debug	调试级别，服务运行的状态信息和错误信息详细显示，信息越多
# info	信息级别，只显示重要的运行信息和错误信息
# notice	通知级别，更加重要的信息进行通知说明
# warn	警告级别，可能出现了一些错误信息，但不影响服务运行
# error	错误级别，服务运行已经出现了错误，需要 进行纠正，推荐选择
# crit	严重级别，必须进行修正调整
# alert	严重警告级别，即警告，而且必须进行错误修改
# emerg	灾难级别，服务已经不能正常运行，信息越少

# PS：日志要做切割
```
### ngx_http_core_module
```shell
# 5. nginx服务location作用
# 模块说明：ngx_http_core_module
# location进行匹配uri
# 错误页面优雅显示
location	/oldboy	{
	root	/html/www;
	error_page	404	/oldboy.jpg;
}
location	/oldgirl	{
	root	/html/www;
	error_page	404	/oldgirl.jpg;
}

location详细配置
location = / {	精确匹配，优先级01，最高
}
location / {	默认匹配，优先级04，最低
}
location /documents/ {	按照目录进行匹配，优先级03
}
location ^~ /images/ {	优先匹配、不识别uri信息中符号信息，优先级02
}
location ~* \. (gif|jpg|jpeg) $ {	不区分大小写进行匹配，优先级03
}
```
### http_rewrite_module
```shell
# 6. 利用nginx实现页面跳转功能
# 利用rewrite模块是跳转功能，http_rewrite_module
# rewrite ^/(.*) http://www.oldboy.com/$1 permanent;	重写规则配置
# 跳转方式：
# 永久跳转，permanent，301，会将跳转信息进项缓存
# 临时跳转，redirect，302，不会缓存跳转信息
# 出现无限跳转如何解决：
# 一：利用不同server区块配置打破循环
server {
	server_name oldboy.com;
	rewrite ^/(.*) http://www.oldboy.com/$1 permanent;
}
# 二：利用if判断实现打破循环
if ($host ~* "^oldboy.com$") {
	rewrite ^/(.*) http://www.oldboy.com/$1 permanent;
}
```

## 网站的LNMP架构部署
```shell
# 1.1 mysql部署：
# 1.1.1 安装
yum install mariadb-server mariadb -y
# 补充：数据库初始化过程 mysql_install_db
# --basedir=path，指定mysql程序目录
# --datadir=path，指定数据信息保存目录
# --user=mysql，让mysql管理数据目录 700
# 1.1.2 启动
systemctl start mariadb.service
systemctl enable mariadb.service
# 1.1.3 设置密码
mysqladmin -u root password  'oldboy123'，设置密码
myssql -u root -poldboy123

# 1.2 PHP部署
# 1.2.1 更新yum源、卸载系统自带的PHP软件
yum remove php-mysql php php-fpm php-common
rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
rpm -Uvh https://mirror.webtatic.com/yum/el7/webtatic-release.rpm
# 1.2.2 安装php软件
yum install -y php71w php71w-cli php71w-common php71w-devel php71w-embedded php71w-gd php71w-mcrypt php71w-mbstring php71w-pdo php71w-xml php71w-fpm php71w-mysqlnd php71w-opcache php71w-pecl-memcached php71w-pecl-redis php71w-pecl-mongodb
# 1.2.3 编写配置文件
vim /etc/php-fpm.d/www.conf
user=nginx
group=nginx
# PS：保证nginx进程的管理用户和php服务进程的管理用户保持一致
# 1.2.4 启动php服务
systemctl start php-fpm
```

### LNMP架构的原理
用户访问网站-->nginx（fastcgi_pass）--FastCGI -->（php-fpm -- wrapper） php（php解析器）--> mysql（读取或写入）

### 实现LNMP之间建立关系
```shell
# 3.1 实现nginx+php建立关系
# 3.1.1 编写nginx文件 
location ~\.php$ {
	root /www;
	fastcgi_index index.php;
	fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
	fastcgi_pass 127.0.0.1:9000;
	include fastcgi_params;	变量配置文件
}
# 重启nginx服务
# 3.1.2 编写动态资源文件
vim /html/blog/test_php.php
<?php
phpinfo();
?>
# 3.1.3 进行访问测试
blog.oldboy.com/test_php.php

# 3.2 实现php+mysql建立关系
# 3.2.1 编写php代码文件
vim test_mysql.php
<?php
	$servername="localhost";
	$username="root";
	$password="oldboy123";
	$conn=mysqli_connect($servername,$username,$password);
	if ($conn){
		echo "mysql successful by root !\n";
	}else{
		die("conection failed:".mysqli_connect_error());
	}
?>
```
### 部署搭建网站页面（代码上线）
```shell
# 4.1 获取代码信息（git），使用开源网站代码
# www网站页面：http://www.dedecms.com
# bbs网站页面：http://www.discuz.net/forum.php
# blog网站页面：https://cn.wordpress.org/
# wecenter网站页面：http://www.wecenter.com/?copyright
# 4.2 将代码解压，将解压后信息放入到站点目录中
tar xf wordpress-5.2.1.tar.gz
mv ..
# 4.3 修改站点目录权限
chown -R www.www blog
# 4.4 进行网站页面初始化操作
# 4.5 对数据库服务进行配置
# 创建数据库：create databases wordpress;
# 检查：show databases;
# 创建数据库管理用户：grant all on wordpress.* to 'wordpress'@'localhost' identified by 'oldboy123';
# 检查：select user,host from mysql.user
# 4.6 利用网站发布博文
```
### 上传wordpress主题，报413错误，如何解决？
```shell
# 1. 
# 1.1 修改nginx配置文件
vim blog.conf
server {
	client_max_body_size 50m;	指定用户上传数据的大小限制（默认1m）
}
# 1.2 修改php.ini配置文件
upload_max_filesize=50M	使用php接收用户上传的更大的数据（默认2M）
```

### 如何让LNMP架构和存储服务器建立关系
```shell
# 2.1 查找图片存储位置
# 2.1.1 根据图片链接地址获取图片存储位置
# 2.1.2 使用命令在站点目录中查找
find /html/blog -type f -mmin -5
inotifywait -mrq /html/blog
# 2.2 使web服务器和存储服务器建立关系
# 检查 存储服务是否正常
# 编写存储服务配置文件
showmount -e 172.16.1.31
/data/bbs 172.16.1.0/24
/data/www 172.16.1.0/24
/data/blog 172.16.1.0/24
mkdir /data/{bbs,blog,www}
# 将web服务器blog存储的数据进行迁移，迁移到存储服务器的映射目录
mv /tmp/2019/ /html/blog/wp-content/uploads/

# 默认存储服务器无法存储数据：
# 管理用户无法存储：root_squash --- nfsnobody
# 不同用户无法存储：no_all_squash
# 解决：
# 第一个历程：修改nfs配置文件，定义映射用户为www
useradd www -u 1002
chown -R www /data
# 第二个历程：使用root用户可以上传数据
sed -ri.bak 's#(sync)#\1,anonuid=1002,anongid=1002#g' /etc/exports
```
### 如何让LNMP架构和数据库服务器建立关系？？？
```shell
# 3.1 将web服务器本地数据库数据进行备份
mysqldump -uroot -poldboy123 --all-datebase > /tmp/web_back.sql
# 3.2 将备份数据进行迁移
scp -rp /tmp/web_back.sql 172.16.1.51:/tmp
# 3.3 恢复数据信息
yum install -y mariadb-server mariadb
# 3.4 修改数据库服务器中数据库用户信息
> select user,host from mysql.user;
# 优化：删除无用的用户信息
delete from mysql.user where user="" and host="localhost";
delete from mysql.user where user="" and host="web01";
# 添加：添加新的用户信息
grant all on wordpress.* to 'wordpress'@'172.16.1.%' identified by 'oldboy123';
# 3.5 修改web服务器代码文件信息
vim wp-config.php
define ('DB_HOST','172.16.1.51');
# 3.6 停止web服务器上数据库服务

# 补充：web01代码信息迁移到web02服务器，并且修改了网站域名无法正确访问
# 访问新域名会自动跳转到老的域名
# 方法一：
# 修改wordpress后台设置信息，将后台中老的域名改为新的域名
# 方法二：
# 修改数据库中的一个表，在表中修改一个和域名有管的条目信息
```
## 负载均衡
### 负载均衡概念
```shell
# 反向代理：外网-->代理服务器-->公司网站服务器web
# 正向代理：内网-->代理服务器-->互联网-->web服务器（日本），翻墙
```

### 负载均衡的环境
```shell
# 集群服务器部署：
# PS：集群中每天服务器的配置一模一样
# 企业中：
# 01，现部署好一台LNMP服务器，上传代码信息
# 02，进行访问测试
# 03，批量部署多台web服务器
# 04，将nginx配置文件进行分发
# 05，将站点目录分发给所有主机
```
### 负载均衡服务器部署：

```shell
# 6.1 安装部署nginx软件
# 6.2 编写nginx负载服务配置文件
ngx_http_upstream_module，upstream，负载均衡
ngx_http_proxy_module，proxy_pass，方向代理

upstream oldboy {
	server 10.0.0.7:80;
	server 10.0.0.8:80;
	server 10.0.0.9:80;
}
server {
	listen	80;
	server_name	www.oldboy.com;
	location	/	{
		proxy_pass http://oldboy;
	}
}

# 6.3 实现负载功能测试
# 搭建集群测试环境：
for name in www bbs blog; do echo "$name 10.0.0.7" > /html/$name/wenwen.html; done
for name in www bbs blog; do echo "$name 10.0.0.8" > /html/$name/wenwen.html; done
for name in www bbs blog; do echo "$name 10.0.0.9" > /html/$name/wenwen.html; done
# 修改windows解析文件
10.0.0.5	www.oldboy.com	blog.oldboy.com	bbs.oldboy.com

# 负载均衡访问网站异常排错思路：
# 01，负载均衡 测试后端web节点服务器是否能够正常访问
# 02，负载均衡，利用curl命令访问负载均衡服务器
# 03，打开xshell连接 ping www.oldboy.com
# 04，配置文件编写不正确
```
### 负载均衡配置模块详细说明
```shell
ngx_http_upstream_module，upstream
# 实现不同调度功能
# 01，轮询分配请求（平均）
# 02，权重分配请求（能力越强责任越重）
upstream oldboy {
	server 10.0.0.7:80 weight=3;
	server 10.0.0.8:80 weight=2;
	server 10.0.0.9:80 weight=1;
}
# 03，实现热备份功能（备胎功能）
upstream olbboy {
	server 10.0.0.7:80;
	server 10.0.0.8:80;
	server 10.0.0.9:80 backup;
}
# 04，定义最大失败次数，健康检查参数
max_fails=5
# 05，定义失败之后重发的间隔时间，健康检查参数
fail_timeout=10s，会给失败的服务器一次机会

# 实现不同调度算法
# 01，rr，轮询调度算法
# 02，wrr，权重调度算法
# 03，ip_hash，出现反复登录的时候，可以配置上，但是这个方法没有配置缓存的方式好
# 04，least_conn，根据服务器连接数分配资源

ngx_http_proxy_module，proxy_pass
# 01，访问不同网站地址，不能显示不同的网站页面
proxy_set_header Host $host;	把真实需求访问的地址发给后端服务器
# 02，访问网站用户地址信息无法进行分析统计
proxy_set_header X-Forwarded-For $remote_addr;
# 03，访问负载均衡会出现错误页面，影响用户体验
proxy_next_upstream error timeout http_404 http_502 http_403;

# 1. 负载均衡企业实践应用
# 1.1 根据用户访问的uri信息进行负载均衡
# 1.2 根据用户访问的终端信息显示不同的页面
```

## 高可用服务
```shell
# 3. 如何实现部署高可用服务
# 利用keepalived软件实现
# 作用：
# 3.1 为LVS服务而诞生出来的 k8s+容器技术docker
#                                          keepalived+LVS负载均衡软件（4层）
# 3.2 实现高可用服务功能
```

### 高可用keepalived服务部署流程
```shell
# 4.1 准备高可用服务架构
# 4.2 安装部署keepalived软件（lb01 lb02）
yum install -y keepalived
# 4.3 编写keepalived配置文件
vim /etc/keepalived/keepalived.conf
GLOBAL CONFIGURATION，全局配置部分
VRRPD CONFIGURATION，VRRP协议配置部分
LVS CONFIGURATION，LVS服务管理配置部分

vim /etc/keepalived/keepalived.conf

global_defs {		全局配置部分
	notification_email {	设置发送邮件信息
		XXX
	}
	notification_email_from	XXX
	smtp_server		XXX
	smtp_connect_timeout	30
	router_id			lb01	高可用集群主机身份标识（集群中主机身份标识名称不能重复）
}

vrrp_instance oldboy {	Vrrp协议家族
	state MASTER	标识所有家族中的身份（MASTER/BACKUP）
	interface eth0	指定虚拟IP地址出现在什么网卡上
	virtual_router_id 51	标识家族身份信息，多台高可用服务配置要一致
	priority 100	设定优先级，优先级越高，就越有可能成为主
	advert_int 1	？
	authentication {	实现通讯需要有认证过程
		auth_type PASS
		auth_pass 1111
	}
	virtual_ipaddress {	配置虚拟IP地址信息
		192.168.200.16/24
	}
}
# 4.4 启动keppalived服务
# 。。。
# 4.5 修改域名和IP地址解析
# 。。。
```
### 高可用服务器企业应用
```shell
# 5.1 高可用服务常见异常问题，脑裂问题
# 出现原因，高可用服务器接收不到主服务器发送的组播包，备服务器上会自动生成VIP地址
# 物理原因，高可用集群之间通讯线路出现故障
# 逻辑原因，安全策略阻止
# 如何解决：
# 01，进行监控，并发出告警
# 备服务器出现VIP地址的原因：
# a，主服务器出现故障
# b，出现脑裂问题
# 02，直接关闭一台服务器的keepalived服务

# 5.2 如何实现keepalived服务自动释放vip地址资源
# nginx+keepalived：nginx服务停止，keepalived也必须停止
# 5.2.1 编写监控nginx服务器状态监控
#!/bin/bash
num=`ps -ef | grep -c nginx`
if [ $num -lt 3 ]
then
    systemctl stop keepalived
fi
# 5.2.2 测试监控脚本
# 5.2.3 实时监控nginx服务状态---keepalived配置文件
vrrp_script check_web {
	script "/server/scripts/check_web.sh"	定义需要监控脚本（脚本是执行权限）
	interval 2				执行脚本的间隔时间（秒）
	weight 2				？？？
}

track_script {
	check_web			调用执行你的脚本信息
}

# 5.3 如何设定双主配置
lb01：
vrrp_instance oldboy {
	state MASTER
	...
	virtual_router_id 51
	priority 150
	...
	virtual_ipaddress {
		10.0.0.3/24
	}
}
vrrp_instance oldgirl {
	state BACKUP
	...
	virtual_router_id 52
	priority 100
	...
	virtual_ipaddress {
		10.0.0.4/24
	}
}
lb02：
vrrp_instance oldboy {
	state BACKUP
	...
	virtual_router_id 51
	priority 100
	...
	virtual_ipaddress {
		10.0.0.3/24
	}
}
vrrp_instance oldgirl {
	state MASTER
	...
	virtual_router_id 52
	priority 150
	...
	virtual_ipaddress {
		10.0.0.4/24
	}
}

# 5.4 高可用服务安全访问配置（负载均衡服务）
# 5.4.1 修改nginx负载均衡文件
upstream oldboy {
	server 10.0.0.7:80;
	server 10.0.0.8:80;
	server 10.0.0.9:80;
}
...

# 5.4.2 修改内核文件
echo 'net.ipv4.ip_nonlocal_bind=1' >> /etc/sysctl.conf
sysctl -p

# 5.4.3 重启nginx负载均衡服务
systemctl restart nginx
```