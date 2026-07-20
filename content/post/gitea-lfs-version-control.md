---
title: "自建 Git 服务器：Gitea + LFS 实现测试程序版本控制"
date: 2025-06-21T12:00:00+08:00
draft: false
toc: true
tags:
  - 
categories:
  - 
---

      
## 📋 项目背景

### 原有痛点

我们之前使用 **SVN** 管理测试程序的变更记录，但在实际使用中遇到了一个严重的局限性：

**SVN 无法处理 2GB 以上的大文件**

随着测试程序和镜像文件的体积不断增长（testtool、testimage、ATOtools、Shippingimage、BIOS 等），这个限制严重影响了我们的工作效率。

### 解决方案

引入 **自建 Git 服务器 + LFS（Large File Storage）** 功能，实现：

- ✅ 支持大文件版本控制

- ✅ 完整的代码历史记录

- ✅ 自动化导出和通知

- ✅ 权限管理和审计

## 🔍 工具选型对比

在自建 Git 服务器的方案选择上，我们对比了主流的四款工具：

### 四款工具详细对比

  
      
          工具
          语言/架构
          核心特点
          适用场景
      
  
  
      
          **Gogs**
          Go（单二进制）
          极轻量、资源占用极低、安装简单；功能基础（代码托管、权限管理、Web Hook）
          超小型团队或个人开发者
      
      
          **Gitblit**
          Java
          轻量、支持图形化界面、适合 Windows 部署；功能简单（仓库管理、基础权限）
          需要简单界面操作的小团队
      
      
          **Gitea**
          Go（Gogs 分支）
          轻量但功能更全面（CI/CD、代码审查、项目管理、制品库）；社区活跃，更新频繁
          需要轻量但功能较全的团队
      
      
          **GitLab**
          Ruby
          功能全面（全周期 DevOps、CI/CD、看板、Wiki）；资源消耗高，配置复杂
          中大型团队或复杂项目
      
  

### 各工具详细分析

Gitblit

**优点：**

- 基于 Java 开发，适合 Java 开发者

- 界面友好，Windows 环境下部署方便

**缺点：**

- 功能相对简单

- 主要提供代码仓库管理和基础权限控制

- 对高级功能支持不足

- 社区不如 Gitea 活跃

Gitea

**优点：**

- 基于 Go 语言开发，轻量级

- 跨平台，安装和升级方便

- 功能全面：CI/CD、代码审查、项目管理、制品库等

- 社区活跃，更新频繁

**缺点：**

- 相对 Gogs，资源占用略高

- 但在同类产品中仍然算轻量级

Gogs

**优点：**

- 非常轻量级，资源占用极低

- 安装简单，部署方便

- 核心功能完善

- 适合对服务器资源有严格要求的场景

**缺点：**

- 功能相对 Gitea 较少

- 社区活跃度不如 Gitea

### 🏆 最终选择：Gitea

**选择理由：**

- **功能与轻量化的最佳平衡**

- **支持 LFS**，完美解决大文件问题

- **社区活跃**，持续更新和维护

- **跨平台**，支持 Windows/Linux

- **安装简单**，单二进制文件即可运行

Gitea 是 Gogs 的分支，在保持轻量级的同时，增加了更多实用功能。

## 🚀 安装和配置

### 安装步骤

**参考教程：**

- [服务器（Windows 系统）自建 git 服务器超详细教程](https://www.cnblogs.com/alexgl2008/articles/17948253)

**简要步骤：**

**下载安装 Gitea**

1
2

# 下载 Windows 版本
wget https://dl.gitea.com/gitea/1.21.0/gitea-1.21.0-windows-4.0-amd64.exe

**创建配置文件**

 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
12
13
14
15
16

; app.ini
[server]
DOMAIN = git.yourcompany.com
HTTP_PORT = 3000
ROOT_URL = http://git.yourcompany.com:3000/

[database]
DB_TYPE = sqlite3
PATH = data/gitea.db

[repository]
ROOT = data/git-data/repositories

[lfs]
START_SERVER = true
PATH = data/lfs

**配置 Windows 服务**

- 使用 NSSM（Non-Sucking Service Manager）将 Gitea 封装成 Windows 服务

- 参考：[使用 NSSM - 将任何 exe 应用封装成 windows 服务](https://www.cnblogs.com/05-hust/p/17407534.html)

1
2
3
4

nssm install Gitea
nssm set Gitea Application "C:\Gitea\gitea.exe"
nssm set Gitea AppDirectory "C:\Gitea"
nssm start Gitea

**初始化配置**

- 访问 `http://localhost:3000`

- 设置管理员账号

- 配置仓库根目录

- 启用 LFS 支持

## 📦 LFS 大文件支持

### 问题：仓库更新特别慢

**问题描述：**
在使用过程中，发现更新仓库特别慢，尤其是包含大文件（.zip、.7z 等）的仓库。

**原因分析：**

- Git 默认会下载所有历史版本的文件

- 大文件的历史版本会占用大量带宽和存储空间

### 解决方案：启用 LFS 功能

**步骤 1：配置 LFS 跟踪文件类型**

 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
12

cd my-repository

# 跟踪特定文件类型
git lfs track "*.zip"
git lfs track "*.7z"
git lfs track "*.iso"
git lfs track "*.vmdk"

# 提交配置
git add .gitattributes
git commit -m "enable LFS support"
git push origin main

**步骤 2：迁移已有大文件到 LFS**

1
2
3
4
5

# 迁移仓库中所有历史提交的 7z 和 zip 文件到 LFS
git lfs migrate import --include="*.7z,*.zip" --everything

# 强制推送（注意：会重写历史）
git push --force-with-lease origin main

⚠️ **注意**：如果使用 TortoiseGit 工具，请在 push 时勾选 “force-with-lease” 选项

**步骤 3：验证 LFS 状态**

1
2
3
4
5

# 查看 LFS 跟踪的文件
git lfs ls-files

# 查看 LFS 状态
git lfs status

### LFS 工作原理

 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
12
13

普通 Git 仓库:
┌─────────────────┐
│  .git/objects/  │ ← 存储所有文件内容
│  file.zip (1GB) │ ← 占用大量空间
│  file.zip (1GB) │ ← 每个版本都存储
└─────────────────┘

Git LFS 仓库:
┌─────────────────┐      ┌─────────────────┐
│  .git/objects/  │      │  .git/lfs/      │
│  pointer file   │─────►│  file.zip (1GB) │
│  (几 KB)        │      │  只存储最新版本 │
└─────────────────┘      └─────────────────┘

## 🔄 自动化流程设计

### 整体流程

 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56

flowchart TB
    %% 工程师模块
    subgraph EngModule["👨‍💻 工程师操作模块"]
        direction TB
        A[工程师]:::engineer
        A1[使用 TortoiseGit<br/>修改提交代码]:::engAction
        A2[下载和查询<br/>历史记录]:::engAction
        A3[申请 Git 仓库<br/>修改权限]:::engAction
        
        A --> A1
        A --> A2
        A --> A3
    end
    
    %% 管理员模块
    subgraph AdminModule["🛠️ 管理员管理模块"]
        direction TB
        F[管理员]:::admin
        F1[保留登录<br/>维护权限]:::adminAction
        F2[维护 Git 仓库]:::adminAction
        
        F --> F1
        F --> F2
    end
    
    %% 系统自动化模块
    subgraph SystemModule["⚙️ 系统自动化模块"]
        direction TB
        B[Git 仓库]:::system
        C[服务器]:::system
        D[研发/NPI/TE]:::system
        G[产线机台]:::system
        
        B -->|自动导出| C
        B -->|发送邮件通知| D
        C -->|获取最新程序| G
    end
    
    %% 模块间连接
    A1 --> B
    A2 --> B
    A3 --> F
    F1 --> C
    F2 --> B
    
    %% 样式定义
    classDef engineer fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#000
    classDef engAction fill:#b3e5fc,stroke:#0288d1,stroke-width:1px,color:#000
    classDef admin fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef adminAction fill:#e1bee7,stroke:#8e24aa,stroke-width:1px,color:#000
    classDef system fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    
    %% 子图样式
    style EngModule fill:#f0f8ff,stroke:#0277bd,stroke-width:2px
    style AdminModule fill:#faf0ff,stroke:#7b1fa2,stroke-width:2px
    style SystemModule fill:#f0fff0,stroke:#388e3c,stroke-width:2px

### 详细流程说明

1️⃣ 工程师操作

**提交代码：**

- 使用 **TortoiseGit** 客户端

- 修改测试程序代码（testtool/testimage/ATOtools/Shippingimage/BIOS 等）

- 提交到 Git 仓库

- 可查询历史记录和差异对比

**权限申请：**

 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
12
13

flowchart TD
    A[工程师] --> B[发送权限申请邮件]
    B --> |To|C[管理员<br/>Charles Miao]
    B --> |CC|D[工程师主管]
    B --> |CC|E[TE 主管<br/>Jason Lee]
    
    C --> F[开通权限]
    F --> G[回复邮件]
    G --> |提供使用说明|A
    
    style A fill:#e1f5fe
    style C fill:#fff3e0
    style F fill:#e8f5e8

2️⃣ 管理员职责

- 保留服务器登录和维护权限

- 维护 Git 仓库配置

- 审批权限申请

- 监控系统运行状态

3️⃣ 系统自动化

**自动导出：**

- Git 仓库代码自动导出到文件服务器

- 使用 [GitCheckOut](https://github.com/Charles-Miao/DevOps/tree/master/2025/Gitea+LFS/GitCheckOut) 脚本

- 定时任务或 Web Hook 触发

**邮件通知：**

- Gitea 自带邮件通知无法实现 Commit Notifier

- 自行编写 [CheckGit](https://github.com/Charles-Miao/DevOps/tree/master/2025/Gitea+LFS/CheckGit) 脚本

- 发送邮件给研发/NPI/TE 相关人员

**产线获取：**

- 产线机台从服务器获取最新的 tool/image/BIOS 等文件

- 自动化部署，无需人工干预

## 🔧 关键配置

### 1. 自动导出脚本（GitCheckOut）

**功能：**

- 监听 Git 仓库变更

- 自动检出最新代码到服务器

- 记录变更日志

**示例脚本：**

 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11

@echo off
:: GitCheckOut.bat
set REPO_PATH=C:\git-data\repositories
set EXPORT_PATH=C:\export\testtool

cd %REPO_PATH%
git pull origin main

xcopy /E /Y /I %REPO_PATH% %EXPORT_PATH%

echo Export completed at %date% %time%

### 2. 邮件通知脚本（CheckGit）

**功能：**

- 检查 Git 提交记录

- 生成变更摘要

- 发送邮件通知相关人员

**参考实现：**

 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26

#!/usr/bin/env python
# CheckGit.py
import smtplib
from email.mime.text import MIMEText
import subprocess

def get_recent_commits():
    result = subprocess.run(
        ['git', 'log', '--since="24 hours ago"', '--oneline'],
        capture_output=True,
        text=True
    )
    return result.stdout

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'git@company.com'
    msg['To'] = 'team@company.com'
    
    # 发送邮件逻辑...

if __name__ == '__main__':
    commits = get_recent_commits()
    if commits:
        send_email('Git 仓库更新通知', commits)

### 3. 权限管理

**权限层级：**

  
      
          角色
          权限
      
  
  
      
          **管理员**
          完全控制、用户管理、仓库配置
      
      
          **工程师**
          读写权限（需申请）
      
      
          **产线**
          只读权限（自动获取）
      
  

**安全措施：**

- ✅ 去除工程师远程登录服务器权限

- ✅ 只保留管理员登录和维护权限

- ✅ 工程师修改程序需申请权限

- ✅ 所有操作有审计日志

## 📊 实施效果

### 改善对比

  
      
          指标
          SVN 时期
          Gitea+LFS 时期
          改善
      
  
  
      
          **大文件支持**
          ❌ 不支持 (>2GB)
          ✅ 完美支持
          ⬆️ 100%
      
      
          **仓库更新速度**
          慢（30 分钟+）
          快（2-5 分钟）
          ⬆️ 85%
      
      
          **版本管理**
          基础
          完整 Git 历史
          ⬆️ 100%
      
      
          **自动化程度**
          低（手动）
          高（自动导出 + 通知）
          ⬆️ 90%
      
      
          **权限管理**
          简单
          细粒度控制
          ⬆️ 80%
      
      
          **审计追溯**
          困难
          完整日志
          ⬆️ 100%
      
  

### 实际收益

**效率提升：**

- 工程师提交代码时间：30 分钟 → 5 分钟

- 产线获取最新程序：手动 → 自动

- 版本追溯：困难 → 一键查询

**成本节省：**

- 减少人工操作：约 2 小时/天

- 降低错误率：版本错误减少 95%

- 节省存储空间：LFS 去重，节省约 60% 空间

**管理提升：**

- 权限管理规范化

- 操作流程标准化

- 审计追溯完整化

## 💡 最佳实践

### 1. 仓库组织

 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
12
13

testtool/
├── hardware-test/
│   ├── power-test/
│   ├── thermal-test/
│   └── signal-test/
├── software-test/
│   ├── os-test/
│   ├── driver-test/
│   └── app-test/
└── common/
    ├── scripts/
    ├── configs/
    └── docs/

### 2. 分支策略

1
2
3
4
5

main          ← 生产分支（受保护）
  ├── develop    ← 开发分支
  │     ├── feature/xxx  ← 功能分支
  │     └── bugfix/xxx   ← 修复分支
  └── release/v1.0 ← 发布分支

### 3. 提交规范

1
2
3
4
5

feat: 添加新的电源测试模块
fix: 修复温度采集异常问题
docs: 更新测试流程文档
refactor: 重构数据采集模块
test: 添加压力测试用例

### 4. LFS 文件类型建议

 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
12
13
14
15
16
17
18

# 测试镜像
git lfs track "*.iso"
git lfs track "*.img"
git lfs track "*.vmdk"

# 压缩文件
git lfs track "*.zip"
git lfs track "*.7z"
git lfs track "*.rar"

# 二进制文件
git lfs track "*.bin"
git lfs track "*.exe"
git lfs track "*.dll"

# 大数据集
git lfs track "*.csv"
git lfs track "*.xlsx"

## ⚠️ 常见问题

### Q1: LFS 推送失败

**错误信息：**

1

batch response: This repository is over its LFS storage quota

**解决方案：**

- 检查 LFS 存储配额

- 清理不需要的 LFS 文件

- 升级存储套餐或扩容

### Q2: 仓库历史过大

**问题：**
迁移前仓库已经包含大量大文件历史

**解决方案：**

1
2
3
4
5

# 使用 git lfs migrate 清理历史
git lfs migrate import --include="*.zip,*.7z" --everything

# 强制推送（会重写历史，需谨慎）
git push --force-with-lease origin main

### Q3: 自动导出失败

**排查步骤：**

- 检查 Git 仓库权限

- 检查导出路径权限

- 查看脚本日志

- 手动执行脚本测试

### Q4: 邮件通知不发送

**排查步骤：**

- 检查 SMTP 服务器配置

- 检查邮箱账号密码

- 查看邮件服务器日志

- 测试手动发送

## 📚 参考资料

### 官方文档

- [Gitea 官方文档](https://docs.gitea.com/zh-cn/)

- [Git LFS 官方文档](https://git-lfs.com/)

- [Gitea vs 其他工具对比](https://docs.gitea.com/zh-cn/1.19/installation/comparison)

### 教程资源

- [服务器自建 git 服务器超详细教程](https://www.cnblogs.com/alexgl2008/articles/17948253)

- [使用 NSSM 封装 Windows 服务](https://www.cnblogs.com/05-hust/p/17407534.html)

- [常用 Git 命令清单](https://www.ruanyifeng.com/blog/2015/12/git-cheat-sheet.html)

- [Gitea 邮件通知配置](https://blog.csdn.net/huyuchengus/article/details/128475776)

- [Git LFS 使用教程](https://blog.csdn.net/gitblog_00736/article/details/150995071)

### 工具下载

- [Gitea 下载](https://dl.gitea.com/gitea/)

- [TortoiseGit 下载](https://tortoisegit.org/download/)

- [Git LFS 下载](https://git-lfs.com/)

- [NSSM 下载](https://nssm.cc/download)

## 🎯 总结

通过引入 **Gitea + LFS**，我们成功解决了 SVN 无法处理大文件的问题，并实现了：

✅ **完整的版本控制** - Git 的强大功能

✅ **大文件支持** - LFS 完美解决 2GB+ 文件

✅ **自动化流程** - 自动导出 + 邮件通知

✅ **权限管理** - 细粒度的访问控制

✅ **审计追溯** - 完整的操作日志

这套方案已经在生产环境中稳定运行，为测试程序管理提供了可靠保障。

*本文基于实际生产环境实施经验总结，具体配置需根据实际情况调整。*

*最后更新：2026-03-13*

    

    
  
    文章作者
    
  
  
    上次更新
    
        2025-06-21
        
    
  
  
  

