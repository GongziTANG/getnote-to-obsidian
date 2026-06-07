# 📓 getnote-to-obsidian

[![GitHub stars](https://img.shields.io/github/stars/GongziTANG/getnote-to-obsidian?style=social)](https://github.com/GongziTANG/getnote-to-obsidian/stargazers)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

> 觉得有用，点个 ⭐ **Star** 支持一下 · *If it helps you, a ⭐ means a lot* 🙏

**🇬🇧 English TL;DR** · [中文文档见下 ↓](#-它解决什么问题)

> Auto-archive your voice & text notes from **Get笔记 / Dedao Brain** (biji.com, a popular Chinese
> voice-note app) into **Obsidian** — one-way, safe, idempotent. It even pulls things the app
> doesn't let you export: **full transcripts with speaker labels + timestamps**, and AI **"sprout"
> reports (灵感/insight reports, incl. unsaved ones)**, mapped back to the source note.
>
> **Highlights:** 🎙️ speaker-tagged transcripts · 🌱 AI sprout reports · ➕ child notes ·
> 🗂️ auto-routing into your folders · 🏷️ your own tag library · 💡 daily idea prompts ·
> 🗓️ daily/weekly/monthly time-journals · 📝 traceable logs + rollback.
> **Safety first:** reads Get笔记 only, never edits or deletes your originals. Modular config — swap
> tags / categories / routing for your own. Apache-2.0. See `docs/` for setup, the reverse-engineered
> API, and pitfalls. PRs welcome 🙌

---

> 把 **得到大脑 / Get笔记**（biji.com）里的语音和文字记录，一键、自动、安全地搬进 **Obsidian**——
> 还能补全官方都没在 App 里直接给你的**录音逐字稿、发芽报告**。

如果你也有几百条语音笔记躺在 Get笔记里、想沉淀成自己的第二大脑，这个工具就是给你的。

---

## 😖 它解决什么问题
- Get笔记里录了一堆语音，但**散着、没整理**，时间一长就找不到
- App 里能看逐字稿/发芽报告，但**导不出来**，沉淀不到你自己的知识库
- 手动一条条搬进 Obsidian、还要打标签分类——**太累，坚持不下来**

## ✨ 它帮你做到
| 能力 | 说明 |
|---|---|
| 🗂️ 自动归档 | Get笔记 → 带 frontmatter 的 Markdown，**自动归到该去的文件夹** |
| 🎙️ 录音逐字稿 | 抓官方转写原文，**带「谁说的」+「第几分钟」**，比本地 Whisper 还准 |
| 🌱 发芽报告 | Get笔记的 AI 灵感报告，**连你没存成笔记的也能抓**，精确挂回源笔记 |
| ➕ 追加笔记 | 子笔记一并并入 |
| 🔊 音频原件 | 录音文件下载到本地 |
| 🏷️ 智能打标签 | 按你的标签库打基线标签，保留 Get笔记原始 AI 标签 |
| 📝 可溯源 | 每次归档留日志 + 回滚记录，**做了什么一清二楚** |
| 💡 每日创作灵感 | 从最近笔记长出「今天就能下手」的选题，跨平台铺开（给做内容/IP 的人） |
| 🗓️ 时间日记 | **每日/每周/每月**自动出「时间账 + 反思」——时间花在哪、做了什么、有何思考（柳比歇夫量化 + 曾国藩自省的精神） |

> 归档是纯脚本；灵感和日记这类「会思考」的产出，交给一个 AI agent 按 [`playbooks/`](playbooks) 跑——详见 [docs/SCHEDULES.md](docs/SCHEDULES.md)。

归档后，每条笔记长这样（顺序固定）：
```
正文（智能总结 / 章节 / 金句 / 待办）
→ 🪡 创作工作区
→ 🌱 发芽报告
→ ➕ 追加笔记
→ 🎙️ 录音原文（谁说的 + 时间轴）
```

---

## 🚀 5 分钟上手
```bash
# 1. 拿代码 + 装依赖
git clone https://github.com/<你的用户名>/getnote-to-obsidian.git
cd getnote-to-obsidian
pip install pyyaml

# 2. 配凭据（去 biji.com/openapi 申请，详见 docs/SETUP.md）
#    存到 ~/.getnote/config.json: {"api_key":"gk_live_...","client_id":"cli_..."}

# 3. 配置：指向你的 Obsidian 库
cp config/config.example.yaml config/config.yaml
#    打开 config/config.yaml，把 vault 改成你的库路径

# 4. 先预览（不写任何文件）
python scripts/gn_sync.py --dry-run
```
👉 完整安装、怎么拿 token，看 **[docs/SETUP.md](docs/SETUP.md)**。

---

## 📖 使用
跑完一轮归档，按顺序执行（每步都幂等，可反复跑、不会重复）：
```bash
python scripts/gn_sync.py        # ① 拉新笔记 → md（暂存）+ 下音频 + 回写去重标签
python scripts/gn_route.py       # ② 按你的规则归到正确文件夹 + 写日志
python scripts/gn_transcript.py  # ③ 补录音逐字稿（说话人+时间轴）
python scripts/gn_enrich.py      # ④ 补追加笔记
python scripts/gn_sprout.py --all # ⑤ 补发芽报告（需 web token）
```
**想全自动？** 把这 5 行放进系统定时任务（cron / launchd），每天跑一次即可。

常用参数：`--dry-run`（只预览）、`--limit N`（只处理最近 N 条）、`--no-audio`（不下音频）。

---

## 🧩 你能改什么（模块化，个性化都在 `config/`）
| 改这个文件 | 控制 |
|---|---|
| `config/config.yaml` | 库路径、平台、功能开关、凭据位置 |
| `config/tags.yaml` | **标签库**——整套换成你自己的分类法 |
| `config/categories.yaml` | 内容分类 + 关键词 |
| `config/routing.yaml` | 哪类笔记进哪个文件夹（敏感目录可标记） |
脚本核心逻辑稳定，**你只动 `config/`**。你的配置会覆盖 `*.example.yaml`，且不会进仓库。

---

## ❓ 常见问题
**会动到我 Get笔记里的原始内容吗？** 不会。本工具**单向、只读 Get笔记**，只在 Obsidian 里新建/移动/追加文件、只给 Get笔记**新增**一个去重标签——**绝不删除或修改你的原始笔记**。

**安全吗？凭据会泄露吗？** 凭据只存在你本地（`chmod 600`），已 `.gitignore`，不入仓库、不上传任何第三方。

**重复跑会重复归档吗？** 不会。靠「本地状态 + 源侧标记」双重去重，幂等。

**发芽报告为什么要额外的 web token？** 因为「发芽」走的是网页版内部接口，开放 API 不提供。详见 [docs/API.md](docs/API.md)。不需要发芽可以不配。

**会不会把我的敏感内容（医疗/财务）乱放？** 路由规则里可把这类标 `sensitive`，工具只会**标记进日志请你复核**，不擅自细分。

---

## 🤝 一起维护（求同行者）
坦白讲：录音原文、发芽这些功能依赖对 Get笔记接口的**逆向**，官方一更新就可能失效。
靠一个人追着修很吃力——**所以这个项目从第一天就是为「一起维护」准备的**。

- 哪个功能失效了？开个 issue 贴上报错，就帮了大忙
- 会抓包/写点 Python？`docs/API.md` 把端点和逆向方法都记下来了，照着修很快
- 你的标签库/路由打磨得好？欢迎贡献成示例给别人借鉴

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。作者也只是个想把几百条语音笔记沉淀下来的普通用户，
把摸索出来的东西整理出来分享——不完美，欢迎一起打磨。觉得有用，点个 ⭐ 让更多人和更多维护者找到它。

## 📚 文档
- [docs/SETUP.md](docs/SETUP.md) — 安装、凭据、怎么拿 token（含踩坑）
- [docs/API.md](docs/API.md) — 逆向整理的 Get笔记 API 参考
- [docs/SCHEDULES.md](docs/SCHEDULES.md) — 每日/每周/每月自动化日程（灵感、时间日记）
- [docs/PITFALLS.md](docs/PITFALLS.md) — 踩过的坑 & 设计反思
- [playbooks/](playbooks) — 灵感 / 时间日记 的生成说明书（给 AI agent 用）
- [SKILL.md](SKILL.md) — 作为 AI Agent（Claude/ChatGPT 等）的 skill 使用

## ⚖️ 声明
非官方项目。录音原文 / 发芽走的是 Get笔记 web 内部接口，**仅用于导出你自己的数据**，请遵守 Get笔记服务条款；接口随官方变动可能失效。

## 🙏 关于作者
本项目由 **[@GongziTANG](https://github.com/GongziTANG)（唐公子）** 创作——从逆向接口、设计架构到写文档，
全程**在 AI 辅助下完成**。公众号：**唐公子派**。
> Created by 唐公子 ([@GongziTANG](https://github.com/GongziTANG)), with AI assistance.

## License
**Apache License 2.0** — 见 [LICENSE](LICENSE) 与 [NOTICE](NOTICE)。© 2026 **唐公子 (GongziTANG)**。
> 你可以自由使用、修改、再分发（含商用），但**须保留作者署名（LICENSE + NOTICE）并声明你的改动**。
> 这是为了在最大化传播的同时，**尊重原作者署名**。喜欢的话点个 ⭐ Star 支持一下作者 🙏
> You may freely use, modify, and redistribute (incl. commercially), provided you **retain the author's
> attribution** (LICENSE + NOTICE) and state your changes. If it helps you, a ⭐ means a lot 🙏
