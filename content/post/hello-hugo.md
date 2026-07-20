---
title: "Hello Hugo - 本地部署测试"
date: 2026-03-13T12:00:00+08:00
draft: false
toc: true
tags:
  - 
categories:
  - 
---

      🎉 Hello Hugo!

这是我的第一篇文章，使用 **本地 Hugo** 成功发布！

## 📋 配置过程总结

### 1. 安装 Homebrew

1

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

### 2. 安装 Hugo

1

arch -arm64 /opt/homebrew/bin/brew install hugo

### 3. 克隆博客仓库

1

git clone git@github.com:Charles-Miao/blog.git

### 4. 安装主题

1
2

cd blog/themes
git clone https://github.com/olOwOlo/hugo-theme-even.git even

### 5. 创建文章

1

hugo new post/hello-hugo.md

### 6. 本地预览

1

hugo server -D

### 7. 发布

1

./deploy.sh "发布测试文章"

## 🚀 下一步计划

-  写更多技术文章

-  自定义主题样式

-  添加图片资源

-  配置自定义域名

-  添加评论系统

## 💡 关于博客

这是我的个人技术博客，主要分享：

- **DevOps** 实践经验

- **硬件测试** 自动化方案

- **编程技巧** 和最佳实践

- **系统管理** 心得

*最后更新：2026-03-13*

*使用 Hugo + Even 主题构建*
    

    
  
    文章作者
    
  
  
    上次更新
    
        2026-03-13
        
    
  
  
  

