---
title: "Linux基础 - Part6"
date: 2021-06-14T10:16:52+08:00
description: ""
draft: false
tags: [Linux]
categories: [运维]
---

# 主要内容

- ssh
- ansible

<!--more-->

> [详细笔记](https://github.com/Charles-Miao/Linux/blob/master/Linux%E5%9F%BA%E7%A1%80/%E7%AC%94%E8%AE%B032~36.txt)

## ssh

```shell
# ssh远程连接的方式
# 1. 基于口令的方式
# 2. 基于秘钥的方式

# 基于秘钥连接的部署步骤
ssh-keygen -t dsa
ssh-copy-id -i /root/.ssh/id_dsa.pub root@172.16.1.41
ssh 172.16.1.41

#批量分发秘钥
#!/bin/bash
for ip in 31 7 41
do
	ssh-copy-id -i /root/.ssh/id_dsa.pub root@172.16.1.$ip
done

#免交互分发秘钥
yum install -y sshpass

#!/bin/bash
for ip in {1..100}
do
	sshpass -p 123456 ssh-copy-id -i /root/.ssh/id_dsa.pub root@172.16.1.$ip "-o StrictHostKeyChecking=no" &>/dev/null
	echo -e "host 172.16.1.$ip success."
done

#ssh服务配置文件
vim /etc/ssh/ssh_config

Port 22
ListenAddress 0.0.0.0
PermitEmptyPasswords no
PermitRootLogin yes
GSSAPIAuthentication no
UseDNS no

# ssh远程服务防范入侵
# 1. 用秘钥，不用密码
# 2. 防火墙封闭ssh，指定源ip限制（局域网）
# 3. 开始ssh只监听本地内部ip
# 4. 尽量不使用外网ip
# 5. 最小化授权，最小化安装软件
# 6. 监控重要文件和文件夹
# 	/etc/passwd md5sum
# 	inotify /bin
# 7. 加锁 chattr +i

#ssh相关的命令
ssh-keygen
ssh-copy-id
sshpass
ssh
scp
sftp
ls
cd
lls
lcd
get
put
help
bye
```

## ansible

### ansible批量管理服务部署
```shell
yum install ansible -y
#编写主机清单文件
vim /etc/ansible/hosts
#测试是否可以管理多个主机
ansible all -a "hostname"
```

### ansible服务架构信息
```shell
# 1. 主机清单配置
# 2. 软件模块信息
# 3. 基于秘钥连接主机
# 4. 主机需要关闭selinux
# 5. 软件剧本功能
```

### ansible模块应用
ansible官方网站：https://docs.ansible.com/

#### command

```shell
ansible	oldboy		-m		command	-a			'hostname'
#命令	主机组模块名	指定模块参数	模块名称		指定模块执行动作参数	批量执行操作动作

#扩展应用：
#chdir，切换目录
ansible 172.16.1.31 -m command -a "chdir=/tmp touch oldboy.txt"

#creates，如果文件存在，则不执行命令
ansible 172.16.1.31 -m command -a "creates=/tmp/hosts touch oldboy.txt"

#removes，如果文件存在，则执行命令
ansible 172.16.1.31 -m command -a "removes=/tmp/hosts touch oldboy.txt"

# 注意事项：
# 有些符号信息无法识别：< > | ; &
```
#### shell（万能模块），命令类似command，所有符号都可以识别

```shell
# shell模块
# PS：有时剧本不能反复执行！！！
```
#### script（万能模块），参数功能类似command模块

#### copy，将数据信息进行批量分发

```shell
ansible 172.16.1.31 -m copy -a "src=/etc/hosts dest=/etc/"

# 扩展用法：
# 1. 修改文件属主和属组信息
ansible 172.16.1.31 -m copy -a "src=/etc/hosts dest=/etc/ owner=oldboy group=oldboy"

# 2. 修改文件的权限信息
ansible 172.16.1.31 -m copy -a "src=/etc/hosts dest=/etc/ mode=1777"

# 3. 对远程文件进行备份
ansible 172.16.1.31 -m copy -a "src=/etc/hosts dest=/etc/ backup=yes"

# 4. 创建一个文件并直接编辑文件信息
ansible 172.16.1.31 -m copy -a "content='oldboy123' dest=/etc/rsync.password"

# 自行研究：remote_src directory_mode local_follow
```
#### file，设置文件属性信息

```shell
ansible 172.16.1.31 -m file -a "dest=/etc/hosts owner=oldboy group=oldboy mode=666"

# 扩展用法：
# state
# =absent，删除文件 
# =directory，创建一个目录
# =file，检查创建的数据信息是否存在
# =hard，创建一个硬链接
# =link，创建一个软链接
# =touch，创建一个文件

ansible 172.16.1.31 -m file -a "dest=/oldboy/ state=directory"
ansible 172.16.1.31 -m file -a "dest=/oldboy/oldboy.txt state=touch"
ansible 172.16.1.31 -m file -a "src=/oldboy/oldboy.txt dest=/oldboy/oldboy_hard.txt state=hard"

# 自行研究：recurse，递归
```

#### fetch，和copy模块相反，批量从被管理端拉取数据

#### yum模块

```shell
# name，指定安装软件名称
# state，指定是否安装软件（installed，安装软件；absent，卸载软件）
ansible 172.16.1.31 -m yum -a "name=iotop state=installed"
```
#### service模块
```shell
# name，指定管理的服务名称
# state，指定服务状态（started，restarted，stopped）
# enabled，指定服务是否开机自启动
ansible 172.16.1.31 -m service -a "name=nfs state=started enabled=yes"
```

#### cron模块，批量设置多个主机的定时任务信息
```shell
# minute，设置分钟信息
# hour，设置小时信息
# day，设置日期信息
# month，设置月份信息
# weekday，设置周信息
# job，定义需要干的事情
ansible 172.16.1.31 -m cron -a "name='time sync' minute=0 hour=2 job='/usr/sbin/ntpdate ntp1.aliyun.com >/dev/null 2>&1'"#创建指定任务
ansible 172.16.1.31 -m cron -a "name='time sync' state=absent" #删除指定任务
# PS：ansible可以删除的定时任务，只能是ansible设置好的定时任务
ansible 172.16.1.31 -m cron -a "name='time sync' job='/usr/sbin/ntpdate ntp1.aliyun.com >/dev/null 2>&1' disabled=yes" #注释定时任务
```

#### mount模块，批量进行挂载操作
```shell
# src，需要挂载的存储设备或文件信息
# path，指定目标挂载点目录
# fstype，指定挂载时的文件系统类型
# state（present，mounted，absent，unmounted）
# present，不会实现立即挂载，修改fstab文件，实现开机自动挂载
# mounted，会实现立即挂载，并会修改fstab文件，实现开机自动挂载
# absent，会实现立即卸载，并且会删除fstab文件信息，禁止开机自动挂载
# unmounted，会实现立即卸载，大不会删除fstab文件信息
```
#### user模块，实现批量创建用户
```shell
ansible 172.16.1.31 -m user -a "name=oldboy01"
ansible 172.16.1.31 -m user -a "name=oldboy02 uid=6666"
ansible 172.16.1.31 -m user -a "name=oldboy03 group=oldboy02"
ansible 172.16.1.31 -m user -a "name=oldboy03 groups=oldboy02"
ansible 172.16.1.31 -m user -a "name=rsync create_home=no shell=/sbin/nologin"

#生成密文密码信息：
ansible all -i localhost, -m debug -a "msg={{'密码信息123456' | password_hash ('sha512','oldboy')}}"
yum install -y python-pip
pip install passlib
python -c "from passlib.hash import sha512_crypt; import getpass; print(sha512_crypt.using(rounds=5000).hash(getpass.getpass()))"
#创建用户密码：
ansible 172.16.1.31-m usr -a 'name=oldboy06 password=密文密码'
```

### 剧本编写规范：pyyaml

```shell
# 1. 合理的信息缩进，两个空格表示一个缩进，PS：在ansible中一定不能用tab进行缩进
# 2. 使用冒号后面要有空格信息，以冒号结尾，冒号信息出现在注释说明中，后面不需要加上空格
# 3. 横杠-列表功能
```

```shell
# 编写剧本：
mkdir /etc/ansible/ansible-playbook
vim rsync_server.ymal
- hosts: 172.16.1.41
  tasks:
    - name: 01-install rsync
      yum: name=rsync state=installed
    - name: 02-push config file
      copy: src=/tmp/rsyncd.conf dest=/etc/

# 1. 检查剧本的语法格式
ansible-playbook --synctax-check rsync_server.yaml
# 2. 模拟执行剧本
ansible-playbook -C rsync_server.yaml
# 3. 直接执行剧本
ansible-playbook rsync_server.yaml

# 补充内容：

# 安装libselinux-python让selinux开启状态也可以使用ansible程序

# ansible-doc -l，列出模块使用简介
# ansible-doc -s fetch，指定一个模块详细说明
# ansible-doc fetch，查询模块在剧本中应用方法
```

```shell
vim rsync_server.yaml

- hosts: 172.16.1.41
  tasks:
    - name: 01-install rsync
      yum: name=rsync state=installed
    - name: 02-push conf file
      copy: src=/etc/ansible/server_file/rsync_server/rsyncd.conf dest=/etc/
    - name: 03-create user
      user: name=rsync create_home=no shell=/sbin/nologin
    - name: 04-create backup dir
      file: path=/backup state=directory owner=rsync group=rsync
    - name: 05-create password file
      copy: content=rsync_backup:oldboy123 dest=/etc/rsync.password mode=600
    - name: 06-start rsync server
      service: name=rsyncd state=started enabled=yes

- hosts: 172.16.1.31,172.16.1.7
  tasks:
    - name: 01-install rsync
      yum: name=rsync state=installed
    - name: 02-create password file
      copy: content=oldboy123 dest=/etc/rsync.password mode=600
    - name: 03-create test file
      file: dest=/tmp/test.txt state=touch
    - name: 04-check test
      shell: rsync -avz /tmp/test.txt rsync_backup@172.16.16.1.41::backup --password-file=/etc/rsync.password

# 剧本编写常见错误：
# 1. 剧本句法规范是否符合
# 2. 剧本中模块使用是否正确
# 3. 剧本中一个name标识下面只能写一个模块任务信息
# 4. 剧本尽量不要大量使用shell
```

#### 主机清单配置方式：

```shell
# 1. 分组配置主机信息
[web]
172.16.1.7
172.16.1.8
[data]
172.16.1.31
# 2. 主机名符号匹配配置
[web]
172.16.1.[7:9]
# 3. 跟上非标准端口
[web]
web01:52113
# 4. 主机使用特殊变量
[web]
web01 ansible_ssh_host=172.16.1.7 ansible_ssh_port=52113 ansible_ssh_user=root ansible_ssh_pass=123456
# 5. 主机组嵌入配置
[rsync:children]
rsync_server
rsync_client
[rsync_server]
172.16.1.41
[rsync_client]
172.16.1.7

[web:vars]
ansible_ssh_host=172.16.1.7
ansible_ssh_port=52113
ansible_ssh_user=root
ansible_ssh_pass=123456
[web]
web01
```

#### 编写剧本的重要功能：

```shell
# 1. 在剧本中设置变量信息
# 1.1 在剧本中编写
vars:
  oldboy01: data01
  oldboy02: data02
  #{{ oldboy01 }}
# 1.2 在命令行中进行指定
ansible-playbook -e backupdir=/data -e passfile=rsync-password rsync_server.yaml
# 1.3 在主机清单文件中编写
[oldboy]
oldboy01=data01
oldboy02=data02

# 优先级：
# 1. 命令行中进行指定
# 2. 剧本中变量设置
# 3. 主机清单变量设置
```
```shell
# 2. 剧本设置注册功能，执行剧本时，可以显示输出命令结果信息

- hosts: oldboy
  tasks:
    - name: check server port
      shell: netstat -lntup
      register: get_server_port
    - name: display port info
      debug: msg={{ get_server_port.stdout_lines }}
```
```shell
# 3. 剧本中设置判断信息

- name: 03-create test web file
  file: dest=/tmp/test_web.txt state=touch
  when: (ansible_hostname == web01)

# 获取内置变量方法：
ansible oldboy -m setup -a "filter=ansible_hostname"
# 获取子信息方法：
ansible_etho0[ipv4]
```
```shell
#4. 设置循环

- hosts: all
  remote_user: root
  tasks:
    - name: Add Users
      user: name= {{ item.name }} groups={{ item.groups }} state=present
      with_items:
        - { name: 'testuser1', groups: 'bin' }
        - { name: 'testuser2', groups: 'root'}

# 剧本排错思路：
# 1. 找到剧本中出现问题的关键点
# 2. 剧本中操作转换成模块进行操作
# 3. 讲模块的功能转换成模块进行操作
```
```shell
# 5. 设置错误
ignore_errors: yes
```
```shell
# 6. 设置标签
tags: t1

ansible-playbook -t t1 rsync_server.yaml
```
```shell
#7. 设置触发
      notify: restart rsync server
  handlers:
    - name: restart rsync server
      servcie: name=rsyncd state=restarted
```
```shell
#8. 将多个脚本进行整合
# 1. include_tasks
- hosts: all
  remote_user: root
  tasks:
    - include_tasks: f1.yml
    - include_tasks: f2.yml
# 2. include
- include: f1.yml
- include: f2.yml
# 3. import_playbook（最优）
- import_playbook: f1.yml
- import_playbook: f2.yml
```
```shell
# 剧本编写问题：
# 1. 目录结构不规范
# 2. 编写的任务如何重复调用
# 3. 服务端配置文件改动，客户端参数也自动变化
# 4. 汇总剧本中没有显示主机角色信息
# 5. 一个剧本内容信息过多，不容易进行阅读
```
#### 角色方式编写剧本：
```shell
# 1. 规范目录结构
cd /etc/ansible/roles
mkdir {rsync,nfs}
mkdir {nfs,rsync}/{vars,tasks,templates,handlers,files}
# files，保存需要分发文件目录
# handlers，保存触发器配置文件
# tasks，保存要执行的动作信息文件
# templates，保存需要分发模板文件
# vars，保存变量信息文件
# 2. 编写文件流程图：
# 2.1 编写tasks中的main.yml文件
# 2.2 编写vars目录中的main.yml文件
# 2.3 编写files目录中的文件
# 2.4 编写handlers目录中的main.yml文件
# 3. 编写一个主剧本文件
vim site.yml
- hosts: nfs_server
  roles:
    - nfs-server
```