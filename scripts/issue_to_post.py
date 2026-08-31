#!/usr/bin/env python3
"""把带 publish 标签的 Issue 转成 _posts/ 下的一篇文章。

标签在 = 已发布，标签去掉 = 下架。文章文件名用 Issue 编号，所以
反复编辑同一个 Issue 只会更新同一篇文章，不会产生重复。
"""
import glob
import json
import os
import re
import sys

POSTS = "_posts"
PUBLISH_LABEL = "publish"
CATEGORIES = {
    "个人交易记录": "trades",
    "读书笔记": "books",
    "视频笔记": "videos",
}
# Issue 表单对可选空字段填的占位符
BLANK = {"_No response_", "_无响应_", ""}


def parse_sections(body):
    """Issue 表单的正文形如 '### 分类\n\n个人交易记录\n\n### 摘要\n...'"""
    out, key, buf = {}, None, []
    for line in (body or "").splitlines():
        if line.startswith("### "):
            if key is not None:
                out[key] = "\n".join(buf).strip()
            key, buf = line[4:].strip(), []
        else:
            buf.append(line)
    if key is not None:
        out[key] = "\n".join(buf).strip()
    return out


def clean(v):
    v = (v or "").strip()
    return "" if v in BLANK else v


def yaml_str(v):
    """front matter 里安全地放一个字符串"""
    return '"' + str(v).replace("\\", "\\\\").replace('"', '\\"') + '"'


def existing_file(num):
    hits = glob.glob(os.path.join(POSTS, f"*-issue-{num}.md"))
    return hits[0] if hits else None


def next_seq(current_file):
    """已有文章沿用原编号；新文章取当前最大编号 +1，保证编号不因编辑而变。"""
    if current_file and os.path.exists(current_file):
        with open(current_file, encoding="utf-8") as f:
            m = re.search(r"^seq:\s*(\d+)", f.read(), re.M)
            if m:
                return int(m.group(1))
    used = []
    for p in glob.glob(os.path.join(POSTS, "*.md")):
        with open(p, encoding="utf-8") as f:
            m = re.search(r"^seq:\s*(\d+)", f.read(), re.M)
            if m:
                used.append(int(m.group(1)))
    return max(used, default=0) + 1


def main():
    with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as f:
        issue = json.load(f)["issue"]

    num = issue["number"]
    labels = {l["name"] for l in issue.get("labels", [])}
    current = existing_file(num)

    # 标签不在了 —— 下架
    if PUBLISH_LABEL not in labels:
        if current:
            os.remove(current)
            print(f"下架：{current}")
            return 0
        # 明明是用笔记表单填的，却没带上标签：多半是仓库里还没建 publish 标签
        if "### 分类" in (issue.get("body") or ""):
            print(
                f"::warning::这条 Issue 看起来是用笔记表单填的，但没有 {PUBLISH_LABEL} 标签，"
                f"所以没有发布。请在仓库 Issues → Labels 里新建一个名为 {PUBLISH_LABEL} 的标签，"
                f"然后给这条 Issue 打上它。"
            )
        else:
            print(f"没有 {PUBLISH_LABEL} 标签，跳过")
        return 0

    sec = parse_sections(issue.get("body", ""))
    cat_label = clean(sec.get("分类"))
    cat = CATEGORIES.get(cat_label)
    if not cat:
        print(f"::error::分类无法识别：{cat_label!r}。可选值：{list(CATEGORIES)}")
        return 1

    content = clean(sec.get("正文"))
    if not content:
        print("::error::正文是空的")
        return 1

    title = (issue.get("title") or "").strip() or f"未命名 #{num}"
    date = issue["created_at"][:10]
    seq = next_seq(current)

    fm = [
        "---",
        f"title: {yaml_str(title)}",
        f"cat: {cat}",
        f"seq: {seq}",
        f"date: {date}",
    ]
    summary = clean(sec.get("摘要"))
    if summary:
        fm.append(f"summary: {yaml_str(summary)}")
    pl = clean(sec.get("盈亏"))
    if pl:
        fm.append(f"pl: {yaml_str(pl)}")
    fm += [f"issue: {num}", "---", "", content, ""]

    os.makedirs(POSTS, exist_ok=True)
    target = os.path.join(POSTS, f"{date}-issue-{num}.md")
    # 改了日期就把旧文件挪走，避免同一个 Issue 留下两份
    if current and current != target:
        os.remove(current)
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(fm))
    print(f"已写入：{target}（No.{seq:03d}，分类 {cat}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
