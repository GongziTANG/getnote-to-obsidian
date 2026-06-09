# 自动化日程（每日 / 每周 / 每月）

本工具不只「归档」，还能让你的第二大脑**自己生长**：每天出创作灵感、每天/周/月出反思日记。
归档脚本是纯 Python；下面这些「会思考」的产出，建议交给一个 AI agent（如 Claude、ChatGPT 等）按 playbook 跑。

## 建议节奏
| 频率 | 任务 | 用什么 |
|---|---|---|
| 每天凌晨 | 归档全流程 | `gn_sync → gn_route → gn_transcript → gn_enrich → gn_sprout` |
| 每天早上 | **今日创作灵感清单** | AI 读 `playbooks/DAILY_INSPIRATION.md` |
| 每天晚上 | **时间日记**（量化时间账 + 反思） | `gn_timedata.py` + AI 读 `playbooks/TIME_REFLECTION.md` |
| 每周 | **周记** | 同上，`--since 周一 --until 周日` |
| 每月 | **月记** | 同上，上一自然月 |

## 怎么落地
- **纯归档**：系统 cron / launchd 直接跑 5 个归档脚本即可。
- **会思考的产出**（灵感/日记/周记/月记）：需要一个 LLM agent。
  - 如果你用某个 AI agent（如 Claude 桌面端/Code 等），把每个 playbook 配成一个定时任务，让它按 playbook 取数→生成→写回库→（可选）推回 Get笔记，手机就能看。
  - playbook 在 `playbooks/`，是「怎么生成」的说明书，换成你的口味即可。

## 让它真正无人值守跑（可靠性 · 重要）

很多人会把归档配成「AI 桌面端的定时任务」就以为搞定了。**坑在这**：App 内定时任务依赖宿主 App 在那一刻正在运行、且机器没睡——凌晨的任务几乎必然被睡眠错过，而且**错过不补跑**。任务全绿，产出却是空的（详见 [PITFALLS](PITFALLS.md) 第 8 条）。

**纯归档（5 个 Python 脚本）建议交给 OS 级调度**，机器唤醒后能补跑错过的：

- **macOS（launchd）**：写一个 wrapper 脚本依次跑 `gn_sync→route→transcript→enrich→sprout`，再做 git 快照；用 `~/Library/LaunchAgents/<label>.plist` 的 `StartCalendarInterval` 触发。
- **Linux**：`systemd` user timer，或 cron（cron 不补跑，建议 systemd timer + `Persistent=true`）。

**会遇到的 TCC 坑（macOS）**：launchd 跑的 `python3` 能写 `~/Downloads`（若已授予完全磁盘访问），但同脚本里的 `/usr/bin/git` 会被拒。破法见 `scripts/gn_snapshot.py`——**让 git 由已授权的 python 子进程发起，借道授权**，无需手动给 git 单独授权。

**怎么确认它真在跑**：别看"任务状态"，看**产出痕迹**——今天的归档日志生成了吗？`git log` 有没有当天的自动快照？这是检验一切自动化的唯一可靠标准。

> 「会思考」的产出（灵感/日记）需要 LLM agent，没法纯脚本化；要么保证 agent 常驻 + 机器定时唤醒，要么用 agent 的 CLI 形态（如无头调用）交给 launchd。

## 灵感 / 反思 是怎么来的
- **创作灵感**：从最近的笔记里，长出「今天就能下手」的选题，跨平台跨类别铺开。
- **时间日记**：`gn_timedata.py` 先算出「时间花在哪、各类多少」（柳比歇夫式量化），AI 再据此写量化时间账 + 反思（曾国藩式向内自省）。短而有重量。

> 这些 playbook 默认偏「个人成长 / 内容创作」口味，你可以改成任何风格（工作复盘、学习追踪、健身日志……）。
