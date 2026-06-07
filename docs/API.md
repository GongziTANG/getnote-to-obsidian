# Get笔记 / 得到大脑 API 参考（逆向整理）

> 本项目逆向梳理出的接口。分两层：**开放 API**（官方 key，文档化）和 **web 内部 API**
> （网页登录态，未文档化但很有用，如「发芽」）。仅用于个人数据的自助导出。

## 一、开放 API（official）
- Base：`https://openapi.biji.com`
- 认证：Header `Authorization: Bearer <api_key>` + `X-Client-Id: <client_id>`
- 申请：https://www.biji.com/openapi → 得 `gk_live_...` key + `cli_...` client id
- 官方 CLI：`npm i @getnote/cli`（`getnote` 命令）；**注意 CLI 会丢弃未知字段**（见下）

常用端点（`/open/api/v1/resource/...`）：

| 端点 | 方法 | 说明 |
|---|---|---|
| `note/list` / `notes --all` | GET | 列笔记（分页 has_more/next_cursor） |
| `note/detail?id=<id>` | GET | 笔记详情 |
| `note/save` | POST | 新建笔记 |
| `note/tags/add` | POST | 加标签 |
| `recall?query=` | GET | 语义搜索 |
| `rate-limit/quota` | GET | 配额 |

`note/detail` 的 **raw JSON** 里有 CLI 看不到的关键字段：
- **`audio.original`** —— 录音**逐字稿全文**，带说话人(`🟢 说话人1`)+时间轴(`[00:00:31]`)。
- **`children_ids`** —— 「追加笔记」（子笔记）id 列表。
- `attachments[].url` —— 录音音频文件 URL（umiwi CDN，有时效）。
> 因 CLI 把 JSON 反序列化进固定结构、丢弃未知字段，**必须直连 raw API** 才能拿到这些。

## 二、web 内部 API（「发芽」等，需网页登录 token）
- Base：`https://notes-api.biji.com`
- 认证：Header `Authorization: Bearer <web_token>` + `X-Appid: 3`
- token 从浏览器 `localStorage["token"]` 取（见 SETUP.md）；**30 分钟过期**。
- 续期：`POST /account/v2/web/user/auth/refresh` body `{"refresh_token": "..."}` → 新 token。
  `refresh_token` 约 3 个月有效，可无人值守自动续。

「发芽报告」(sprout) 相关：

| 端点 | 方法 | 说明 |
|---|---|---|
| `/voicenotes/web/user/sprouts/page_by_note?single_note_id_str=<note_id>&limit=20` | GET | **按源笔记**列出其全部发芽（含未存成笔记的）。`limit` 最大 20；参数是 `single_note_id_str` 不是 note_id |
| `/voicenotes/web/user/sprout/detail?sprout_id=<id>` | GET | 发芽**全文**（list 接口的 content 为空，需此接口取） |
| `/voicenotes/web/user/sprouts/today_tasks` | GET | 今日发芽任务 |
| `/voicenotes/web/user/sprouts/month_summary` | GET | 月度发芽用量 |
| `/voicenotes/web/user/sprouts/task/trigger` | POST | 触发发芽 `{note_ids, type:"single_note"}` |

返回外层结构：`{"h":{"c":0,"e":""},"c":{...}}`。`h.c==0` 成功；`h.e=="LoginRequired"` 需刷新 token。

> ⚠️ 内部 API 非官方承诺，随时可能变。仅用于导出**你自己**的数据，遵守 get笔记服务条款。
