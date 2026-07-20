---
title: "Hello Hugo - 本地部署测试"
date: 2026-03-13T12:00:00+08:00
draft: false
toc: true
tags:
  - Hugo
  - 博客
  - 静态站点
categories:
  - 技术
---

> **摘要**：本文记录了基于 Hugo + Even 主题的个人博客本地部署过程，包含环境配置、主题安装、文章管理以及本地预览等步骤。

## 背景

之前的博客系统使用起来不太方便，想换一个更轻量、更可控的方案。调研了一圈后决定用 **Hugo + GitHub Pages** 的方式。

## 配置过程总结

### 1. 安装 Hugo

在 macOS 上通过 Homebrew 安装：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
arch -arm64 /opt/homebrew/bin/brew install hugo
```

### 2. 克隆博客仓库

```bash
git clone git@github.com:Charles-Miao/blog.git
```

### 3. 安装 Even 主题

Even 是一个简洁的 Hugo 主题：

```bash
cd blog/themes
git clone https://github.com/olOwOlo/hugo-theme-even.git even
```

### 4. 创建测试文章

```bash
hugo new post/hello-hugo.md
```

### 5. 本地预览

```bash
hugo server -D
```

然后浏览器访问 `http://localhost:1313` 即可预览效果。

## 发布流程

修改 `config.toml` 配置后，执行：

```bash
hugo -d ../Charles-Miao.github.io
```

然后提交两个仓库并推送到 GitHub。

## 下一步计划

- 写更多技术文章
- 自定义主题样式
- 添加图片资源
- 配置自定义域名
- 添加评论系统

---

✅ 博客部署完成，后续持续更新！
