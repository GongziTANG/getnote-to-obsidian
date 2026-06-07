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

## 灵感 / 反思 是怎么来的
- **创作灵感**：从最近的笔记里，长出「今天就能下手」的选题，跨平台跨类别铺开。
- **时间日记**：`gn_timedata.py` 先算出「时间花在哪、各类多少」（柳比歇夫式量化），AI 再据此写量化时间账 + 反思（曾国藩式向内自省）。短而有重量。

> 这些 playbook 默认偏「个人成长 / 内容创作」口味，你可以改成任何风格（工作复盘、学习追踪、健身日志……）。
