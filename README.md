# Tingguo.github.io

<https://tingguo.github.io> 的源码 — 个人交易学习笔记，Jekyll + GitHub Pages。

## 怎么加一篇新笔记（推荐：在网页上写，不碰代码）

打开仓库的 **Issues → New issue → 「写一篇笔记」**，填表单提交即可。一两分钟后站点自动更新。

- **正文里截图直接 Ctrl+V 粘贴**，图片会自动上传
- 想改文章：回去**编辑那个 Issue**，站点跟着更新，编号不会变
- 想下架文章：**去掉 Issue 上的 `publish` 标签**
- 分类用表单里的下拉框选，不用记任何格式

背后是 [`.github/workflows/publish-note.yml`](.github/workflows/publish-note.yml) 调用
[`scripts/issue_to_post.py`](scripts/issue_to_post.py)，把 Issue 转成 `_posts/` 下的
Markdown 再提交。只有仓库所有者开的 Issue 会被发布。

### 或者，直接写文件

在 `_posts/` 下新建 `年-月-日-英文短名.md`，开头写好 front matter：

```yaml
---
title: 标题
cat: trades        # trades 个人交易记录 / books 读书笔记 / videos 视频笔记
seq: 4              # 连续编号，接着上一篇往下写
date: 2026-09-01
summary: 一句话摘要，会显示在列表里
---
```

推送到 `main` 后 GitHub Pages 会自动重建，一两分钟生效。

> **注意**：编号字段叫 `seq`，不要改成 `no`。YAML 会把裸键 `no`（以及 `yes`/`on`/`off`/`y`/`n`）解析成布尔值，字段会静默失效、取不到值。

### 交易记录可以额外加一张小票

```yaml
pl: "+4.2%"        # 列表里显示盈亏，带负号自动变绿，正数变红
slip:
  - k: 标的
    v: 600519
  - k: 盈亏
    v: "+4.2%"
```

## 结构

| 路径 | 作用 |
| --- | --- |
| `_config.yml` | 站点标题、简介、三个分类的定义 |
| `index.html` | 首页 |
| `trades.md` `books.md` `videos.md` | 三个分类页 |
| `_posts/` | 所有笔记 |
| `_layouts/` | 页面骨架 |
| `_includes/entries.html` | 条目列表 |
| `_includes/mark.html` | 三个分类图标（SVG） |
| `_includes/tape.svg` | 首页的 K 线装饰条 |
| `assets/css/main.css` | 全部样式 |

## 改分类

分类定义只有一处：`_config.yml` 里的 `categories_meta`。改那里，导航、首页卡片和分类页会一起变。新增分类还需要照着 `trades.md` 建一个对应的页面文件。

## 设计说明

配色按 A 股习惯：**红涨绿跌**。版式取自交易账本 — 左栏是编号和日期，右栏是内容，中间一条竖线。
