---
name: getnote-to-obsidian
description: >-
  把「得到大脑 / Get笔记」的语音与文字记录自动归档进 Obsidian：转成带 frontmatter 的 md、
  下载录音、抓官方录音原文(说话人+时间轴)、追加笔记、发芽报告，按你的标签库与路由规则归位到正确文件夹，
  并产出可溯源日志。模块化、可配置、单向只增不改原始资料。当用户提到 Get笔记/得到大脑/biji、
  导出语音笔记、归档到 Obsidian、录音逐字稿、发芽报告时触发。
license: Apache-2.0
---

# Get笔记 → Obsidian 归档 Skill

## 这个 skill 做什么
把 Get笔记 的内容**单向**同步进 Obsidian，并尽可能补全：录音原文(逐字稿)、追加笔记(子笔记)、
发芽报告(AI 灵感报告，含未存成笔记的)。所有「会变的东西」都在 `config/` 里可换。

## 核心原则（务必遵守）
- **单向 · 只增不改**：只读 Get笔记；只新建/移动/追加归档文件、只新增标签；**绝不删除或编辑用户原始资料**。
- **幂等**：所有脚本可反复跑；靠「state + 源侧标记」双重去重。
- **人在回路**：拿不准的进 staging、敏感内容只标记请用户复核，不替用户做不可逆决定。
- 详见 `docs/PITFALLS.md` 的设计反思。

## 工作流（脚本在 `scripts/`，配置在 `config/`）
1. `gn_sync.py` — 拉新笔记→带 frontmatter 的 md（暂存）；下载录音；回写去重标签。
2. `gn_route.py` — 按 `routing.yaml` 路由到正确文件夹 + 写溯源日志(+回滚 json)。
3. `gn_transcript.py` — 抓 `audio.original` 逐字稿(说话人+时间轴)追加到 md。
4. `gn_enrich.py` — 抓 `children_ids` 追加笔记插入。
5. `gn_sprout.py` — 抓发芽报告(web API，含未存的)精确插入到对应源笔记。
归档 md 结构：`正文 → 创作工作区 → 🌱发芽 → ➕追加笔记 → 🎙️录音原文`。

## 可替换的模块（config/）
- `tags.yaml` — **标签库**（标准分类法，换成你的体系）
- `categories.yaml` — 内容分类 + 关键词
- `routing.yaml` — 分类/关键词 → 文件夹（含敏感目录标记）
- `config.yaml` — 库路径、平台、开关、凭据位置

## 安装 / 凭据
见 `docs/SETUP.md`（开放 API key + 可选的 web token）。API 细节见 `docs/API.md`。

## 给接手的 Agent
读 `docs/PITFALLS.md`（坑）+ `docs/API.md`（接口）+ 本文件即可上手。改个性化只动 `config/`，
核心逻辑别动。任何触及原始数据的删改，先向用户确认。
