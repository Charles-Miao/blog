---
title: "Linux基础 - Part2"
date: 2021-05-25T21:56:36+08:00
description: ""
draft: false
tags: [Linux]
categories: [运维]
---

# 主要内容

- grep
- 系统文件属性
- find
- 系统符号
- 正则符号
- sed
- awk
- 其他知识

<!--more-->

> [详细笔记](https://github.com/Charles-Miao/Linux/blob/master/Linux%E5%9F%BA%E7%A1%80/%E7%AC%94%E8%AE%B013~19.txt)

grep
---

```shell
#筛选
grep "oldboy" /oldboy/test.txt
#筛选前一行
grep -B 1 "oldgirl" /oldboy/test.txt
#筛选后一行
grep -A 1 "oldgirl" /oldboy/test.txt
#筛选前一行和后一行
grep -C 1 "oldgirl" /oldboy/test.txt
#统计出现几次
grep -c "oldgirl" /oldboy/test.txt
```

系统文件属性
---

- 文件类型（-、d、l、c/b、s）
```shell
ln -s /oldboy/oldboy.txt /oldboy/oldboy_link.txt #创建软链接
#ln，link
#-s，soft

#统计目录下面有多少子目录
ll /etc/ | grep -c "^d"
ll /etc/ | grep "^d" | wc -l
```
- 文件权限（r、w、x、-）

- inode

```shell
df -i #查看indoes使用状况
#文件属性信息存储在inode中
#文件名称信息存储在上一级目录的block中
```

- 时间类型：访问信息、修改时间、改变时间（数据属性发生改变）

- 硬链接数

find
---

```shell
find /etc -type f -name "ifcfg-eth0"
find /etc -type f -name "ifcfg*"
find /etc -type f -iname "ifcfg*" #忽略大小写
find /oldboy -type f -size +100 #大于100k的文件
find /oldboy -type f -size -100 #小于100k的文件
find /oldboy -type f -size +1M #大于1M的文件
find /oldboy -maxdepth 1 -type f -name "oldboy" #深入一层找数据
find /oldboy -maxdepth 1 -type f -perm 644 #查找对应权限的文件
#将找出的文件统一删除
find /oldboy/ -type f -name "*.txt" -delete
find /oldboy/ -type f -name "*.txt" -exec rm -rf {} \;
find /oldboy/ -type f -name "*.txt" | xargs rm -f #xargs把一列数据改成一行显示
#找出txt结尾的文件，统一压缩处理
find /oldboy/ -type f -name "*.txt" | xargs tar zcvf /tmp/oldboy.tar.gz
tar zcvf /tmp/oldboy.tar.gz `find /oldboy/ -type f -name "*.txt"`
find /oldboy -type f -mtime +10 -delete #删除历史数据（十天前）
find /oldboy -type f -mtime -10 -delete #删除历史数据（最近十天）
```

系统符号
---

```shell
$ #取变量，行结尾

! #取反
grep -v "^#" /etc/selinux/config #取反，不看开头是#的行

| xargs #管道符号
find /oldboy -tyep f -name "*.txt" | xargs -i cp {} /oldgirl #寻找到的文件拷贝到指定目录（将需要拷贝的内容放到中间{}内）
find /oldboy -type f -name "*.txt" | xargs -t /oldgirl #寻找到的文件拷贝到指定目录（指定目标文件夹）

# #注释

'' #所见即所得（变量不会解析结果）
"" #和''类似，但是会特殊信息进行解析（变量$LANG会解析结果）
``<==>$() #将引号内的命令先执行，将执行结果给外面
没有引号 #和""类似，但是可以直接识别通配符信息

#重定向符号
#>和1> 标准输出重定向
#2> 错误输出重定向
#>> 标准输出追加重定向
#将正确和错误信息保存到一个文件中
echo oldboy >> /oldboy/info.log 2>> /oldboy/info.log
echo oldboy &> /oldboy/info.log
echo oldboy > /oldboy/info.log 2>&1

&& #与逻辑符号，前一个命令执行成功，再执行后一个
|| #或逻辑符号，前一个执行失败，再执行后一个，成功则不执行

* #模糊匹配

{} #生成连续序列信息
echo {1..100}
echo {a..z}
```

正则符号
---

```shell
^ #以什么开头的信息
$ #以什么结尾的信息
ll -F /etc/ | grep /$ #找目录信息
grep -v "^$" #文件中过滤，剔除空行，-v为取反
. #匹配任意一个字符，且只有一个字符
* #匹配前一个字符连续出现了0次或者多次
.* #匹配任意所有信息
#指定具体信息阻止贪婪匹配
grep "^m.*to" ~/oldboy_test.txt

#转义符号\
echo -e "oldboy01\noldboy02"
\n #换行符号
\t #制表符号

[] #匹配多个字符信息
grep "oldb[oe]y" oldboy.txt #匹配出oldboy和oldbey的信息
grep "^[Im]" oldboy.txt #匹配出所有以I和m开头的信息
grep "^[a-Z]" oldboy.txt #找出所有以字母开头的行

[^abc] #表示排除包含a或b或c信息的字符
^[^abc] #排除包含a或b或c字母开头的行

#扩展正则符号（grep和sed不能直接识别，awk、egrep、grep -E、sed -r可以直接识别）
+ #匹配前一个字符连续出现了1次或者多次
grep -Ev "[0-9]+" oldboy.txt #+连续[0-9]数字v取反

| #并且符号，用于匹配多个信息
grep -E "oldboy|oldbey" oldboy.txt #匹配出oldboy和oldbey的信息

() #后项使用前项
echo oldboy{01..10}|xargs -n1 | sed -r 's#(.*)#useradd \1#g'| bash #创建用户oldboy1~10
seq -w 10 | sed -r 's#(.*)#useradd oldboy\1;echo 123456|passwd --stdin oldboy\1#g' | bash #创建完用户，并设定默认密码为123456
echo 123456 | sed -r "s#(.*)#<\1>#g" #<123456>
echo 123456 | sed -r "s#(..)(..)(..)#<\1><\2><\3>#g" #<12><34><56>

{} #可以指定字符连续匹配的次数
x{n,m} #表示前一个字符至少连续出现n次，最多出现m次
x{n} #表示前一个字符正好连续出现了n次
x{n,} #表示前一个字符至少连续出现n次，最多出现多少次不限
x{,m} #表示前一个字符至少连续出现0次，最多出现m次

? #定义匹配前一个字符出现0次或者1次

ip a s eth0 | egrep "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" -o | head -1 #筛选出ip地址，还有多种方法
```

sed
---

> sed命令（善于处理配置文件）

> 字符流编辑工具，按照每行中的字符进行处理操作（PS：vi、vim，全屏编辑工具）

> 擅长对小文件行进行操作、擅长将文件的内容信息进行修改调整和删除、编写脚本（增、删、改、查）

```shell
#1. 查询信息方法（根据行号查询，根据信息查询）

#测试环境：
cat >person.txt<<EOF
101,Charles,CEO
102,Mandy,CTO
103,Mary,COO
104,Alice,CFO
EOF

sed -n '3p' person.txt
sed -n '1,3p' person.txt
sed -n '1p;3p' person.txt

sed -n '/Charles/p' person.txt
sed -n '/Charles/,/Mary/p' person.txt
sed -n '/Charles/p;/Mary/p' person.txt

#2. 添加信息方法
sed '1i100,oldgirl,UFO' person.txt
sed -i '1i100,oldgirl,UFO' person.txt
sed '$a108,oldgirl,UFO' person.txt

p #print，输出信息
i #insert，插入信息，在指定信息前
a #append，附加信息，在指定信息后面
d #delete，删除指定信息
s #substitute，替换
c #替换修改制定的一整行信息
-n #取消默认输出
-r #识别扩展正则
-i #真是编辑文件，将内存信息写入磁盘
-e #识别sed命令多个操作指令
ps #n和i参数同时使用会将文件内容清空

sed -e '/oldboy/ioldgirl' -e '/oldboy/aolddog' person.txt
sed '$a100\n101' person.txt

#3. 删除信息方法
sed '3d' person.txt
sed '2,6d' person.txt
sed '/oldboy/d' person.txt
sed '3d;6d' person.txt
sed '/^$/d' person.txt #删除空行

#4. 修改信息方法
sed 's#test#test2#g' 文件信息
ip a s eth0 | sed -n '3p' | sed -r 's#^.*net(.*)/24.*#\1#g'
ip a s eth0 | sed -rn '3s#^.*net(.*)/24.*#\1#gp'
sed -i.bak 's#test#test2#g' person.txt #在修改的同时生成一个person.txt.bak的备份文件
ls oldboy*.txt | sed -r 's#(.*)txt#mv & \1jpg#g' | bash #批量修改拓展名	
rename .jpg .txt oldboy*.jpg #批量修改拓展名

```

awk
---

> awk命令（善于处理日志文件）

> 擅长对列进行操作、进行数据信息统计（排除、查询、统计）

> ### awk模式概念说明
> #### 普通模式
> 1. 正则表达式作为模式
> 2. 利用标价匹配信息NR==2
> 3. 范围模式NR==2,NR==10
> #### 特殊模式
> BEGIN{}，在awk执行前，可以显示表头，可以用于计算，可以使用内置变量
> END{}，在awk执行之后



```shell
#测试环境：
Miao    Charles    1017635452    :210:21:51

#1. 命令查询信息方法：
#按行查找
awk 'NR==2' awk_test.txt #单行
awk 'NR==2,NR==4' awk_test.txt #连续多行
awk 'NR==2;NR==4' awk_test.txt #不连续多行

#按字符查找
awk '/Xiaoyu/' awk_test.txt
awk '/Xiaoyu/,/Waiwai/' awk_test.txt
awk '/Xiaoyu/;/Waiwai/' awk_test.txt

#高级查找
awk '/Xiaoyu/{print $1,$3}' awk_test.txt #输出Xiaoyu所在行的第一列和第三列
awk '/Charles/{print $NF}' awk_test.txt | awk -F ":" '{print $3}' #输出Charles所在行的最后一列中的第三列
awk -F ":" '/Charles/{print $3}' awk_test.txt #等同于上一个命令
awk -F "[ :]+" '/Charles/{print $1,$2,$(NF-1)}' awk_test.txt
awk '$3~/^41/{print $1,$2,$3}' awk_test.txt #第三列中以41开头的信息
awk '$3~/1$|5$/{print $1,$2,$3}' awk_test.txt #第三列中以1或5结尾的信息
awk '$3~/[15]$/{print $1,$2,$3}' awk_test.txt #同上一个命令
awk '$2~/Xiaoyu/{gsub(/:/,"$",$NF);print $NF}' awk_test.txt #将最后一列替换为$210$21$51输出

awk '$0~/^#|^$/' awk_test.txt #排除空行和注释行

$1 $2 $3 #第1、2、3个
$NF #最后一个
$(NF-n) #倒数第n个
$0 #整行或整列

#2. 对日志信息进行统计或求和
awk '/^$/{i++,print i}' /etc/services #找出空行数
awk '/^$/{i++}END{print i}' /etc/services #找出空行数
awk '$NF~/bash/{i++}END{print i}' /etc/passwd #统计普通用户数
awk '/Failed password/{i++}END{print i}' /etc/secure #统计登录密码错误的次数
awk -F ":" 'BEGIN{print "第一次总额","第三次总额"}{a=a+$2;b=b+$4}END{print a,b}' awk_test.txt #求和
```

其他知识
---

```shell
tail -f
tail -F
#-f：文件被删除或移走，需要进行重新追踪
#-F：文件被删除或移走，不需要进行重新追踪，只要文件恢复回来会继续追踪

yum erase cowsay -y #不建议使用，会直接删除依赖包
rpm -e cowsay --nodeps #推荐使用，不检查依赖直接删除，不会删除依赖包

echo 123456 | passwd --stdin oldboy #免交互创建密码

file /etc/hosts #查看文件类型
which #显示命令所在目录
whereis #显示文件所在目录，以及相关帮助手册
locate ifcfg-eth0 #查看配置档案所在目录
updatedb #建立文件和目录结构对应关系，便于检索

tree /oldboy #显示指定目录中的所有数据和所有结构信息
tree -L 2 / #查看目录层级为2的文件
tree -d /oldboy #只显示目录

tar zcvf /oldboy/oldboy.tar.gz /oldboy/odlyboy
#z 压缩方式为zip
#c 创建
#v 显示压缩过程
#f 指定压缩包文件路径信息
tar zxvf /oldboy/oldboy.tar.gz
#x 提取
tar zcvf /tmp/oldboy.tar.gz ./oldboy --exclude=./oldboy/oldboy.txt
tar zcvf /etm/oldboy.tar.gz /oldboy --exclude-from=/tmp/exclude.txt

diff path1 path2
vimdiff path1 path2

#调整时间格式
date "+%F %T"
date "+%y-%m-%d %H:%M:%S"
date -s "" #设定时间
date +%F -d "+1day" #显示未来和历史时间 
ntpdate ntp1.aliyun.com #时间同步

yum install -y lrzsz #windows和linux文件传输
```


> #### 保护root
> - 修改远程连接端口，修改/etc/ssh/sshd_config
> - 禁止root用户远程登录，修改/etc/ssh/sshd_config（普通用户登录再切换，则可以远程执行root指令	）