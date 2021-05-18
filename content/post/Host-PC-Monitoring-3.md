---
title: "生产电脑智慧化管理 - 有趣的数据分析"
date: 2020-09-09T22:02:30+08:00
description: ""
draft: false
tags: [R,相关性验证]
categories: [数据分析]
---
主要内容：
---
- 提出问题
- 清洗数据
- 相关性验证
- 一些结论

<!--more-->

提出问题
---

- 测试时间是否和电脑的配置和性能相关？

数据清洗
---

测试时间

- 抓取[UIlog](https://github.com/Charles-Miao/blog/blob/master/static/Test-Time-Analysis/raw-data/log.7z)，并使用脚本[computer_test_log.py](https://github.com/Charles-Miao/blog/blob/master/static/Test-Time-Analysis/computer_test_log.py)筛选测试log，并生成csv文件
- 测试时间平均值，剔除两端异常数据，EXCEL函数**TRIMMEAN(array,percent)**
- 测试时间相对值，将测试时间平均值/各站平均值的平均值

电脑配置和性能数据

- Memory/ CPU/ Disk Score直接可以透过捞取历史数据获取
- 平均温度，捞取3天数据中温度最高的50个值的平均值，测试时温度高，不测试时温度低
- 平均CPU Loading，捞取3天数据中CPU最高的50个值的平均值，测试时CPU高，不测试时CPU低
- 平均Memory Loading，通过手动分析Memory貌似不跟随停线状况变化，故捞取3天数据中Memory最低的100个值的平均值

数据清洗结果

![data-filt](https://github.com/Charles-Miao/blog/blob/master/static/Test-Time-Analysis/data_filt.PNG?raw=true)

相关性验证
---

- 使用jupyter Notbook工具和corr方法分析不够直观
- 使用R语言，生成热力图更直观，参考链接：https://www.jianshu.com/p/bb3c55abafe4

```python
data("attitude")
Ca <- cor(attitude)#cor的结果就是矩阵

library(gplots)
library(RColorBrewer)
coul <- colorRampPalette(brewer.pal(8, "PiYG"))(25)#换个好看的颜色
hM <- format(round(Ca, 2))#对数据保留2位小数

heatmap.2(Ca,
trace="none",#不显示trace
col=coul,#修改热图颜色
density.info = "none",#图例取消density
key.xlab ='Correlation',
key.title = "",
cexRow = 1,cexCol = 1,#修改横纵坐标字体
Rowv = F,Colv = F, #去除聚类
margins = c(6, 6),
cellnote = hM,notecol='black'#添加相关系数的值及修改字体颜色
            )
```

所有数据

![all](https://github.com/Charles-Miao/blog/blob/master/static/Test-Time-Analysis/analysis/ALL.png?raw=true)

CT站

![CT](https://github.com/Charles-Miao/blog/blob/master/static/Test-Time-Analysis/analysis/CT.png?raw=true)

CU站

![CU](https://github.com/Charles-Miao/blog/blob/master/static/Test-Time-Analysis/analysis/CU.png?raw=true)

DK站

![DK](https://github.com/Charles-Miao/blog/blob/master/static/Test-Time-Analysis/analysis/DK.png?raw=true)

TT站

![TT](https://github.com/Charles-Miao/blog/blob/master/static/Test-Time-Analysis/analysis/TT.png?raw=true)

一些结论
---

- CT站测试时间和CPU Loading成**强相关**
- CU站测试时间和CPU分数成中等相关
- DK站数据过少，测试时间和CPU Score、CPU Loading、CPU温度、Memory Score、剩余memory成**强相关**
- TT站测试时间和CPU Score、CPU温度、CPU Loading成中等相关
- 整体来看不太容易发现测试时间和电脑性能和配置的相关性，只是和CPU分数成中等相关



参考资料
---

相关系数：

- 0.8-1.0 极强相关
- 0.6-0.8 强相关
- 0.4-0.6 中等程度相关
- 0.2-0.4 弱相关
- 0.0-0.2 极弱相关或无相关 

参考链接：

- https://zhuanlan.zhihu.com/p/74719545

- https://www.biaodianfu.com/python-correlation-analysis.html
- https://medium.com/@lochaiching/%E6%96%87%E7%A7%91%E7%94%9F%E5%AD%A6python%E7%B3%BB%E5%88%9720-%E5%85%B1%E4%BA%AB%E5%8D%95%E8%BD%A6%E6%A1%88%E4%BE%8B2-%E7%9B%B8%E5%85%B3%E6%80%A7%E5%88%86%E6%9E%90-ee3be09de7a7

- https://zhuanlan.zhihu.com/p/114008006
- https://rpubs.com/loness/183681
- https://www.jianshu.com/p/bb3c55abafe4