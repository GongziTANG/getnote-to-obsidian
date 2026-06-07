# 安装与配置（5–10 分钟）

跟着走即可。卡住了看每节末尾的「踩坑」。

## 第 0 步 · 准备
- Python 3.9+：终端跑 `python3 --version` 能看到版本即可
- 装依赖：`pip install pyyaml`
- （可选）官方 CLI，用于列笔记和打标签：`npm install -g @getnote/cli`，然后 `getnote auth login`

## 第 1 步 · 开放 API 凭据（必需）
归档、打标签、抓录音原文都靠它。
1. 浏览器打开 **https://www.biji.com/openapi**，登录，申请一个 API Key
2. 你会拿到两串：`api_key`（`gk_live_...` 开头）和 `client_id`（`cli_...` 开头）
3. 存成文件 `~/.getnote/config.json`：
   ```json
   { "api_key": "gk_live_你的", "client_id": "cli_你的" }
   ```
4. 锁权限：`chmod 600 ~/.getnote/config.json`

> 踩坑：这串 key 是你的私密凭证，别发到任何公开地方、别提交进 git。

## 第 2 步 · web token（只有要抓「发芽报告」才需要）
「发芽」走的是网页版内部接口，需要你的网页登录态。**不需要发芽可跳过本步**。

1. 浏览器登录 **biji.com**，停在**能看到你笔记列表**的页面（不是营销首页）
2. 打开开发者控制台：
   - **Chrome**：按 `⌥ Option + ⌘ + J`（直接弹控制台）
   - **Safari**：先 顶部菜单「Safari → 设置 → 高级 → 勾选‘在菜单栏显示开发菜单’」，再按 `⌥ + ⌘ + C`
3. 在控制台最底下（`>` 那行）粘贴这句，回车：
   ```js
   copy(JSON.stringify(localStorage))
   ```
   - 屏幕弹出红色「源码映射」之类的警告 → **全部无视**，跟你无关
   - 回车后显示 `undefined` → **这是正常的**！`copy()` 本来就返回 undefined，内容已经复制到剪贴板了
4. 新建文本，粘贴（⌘V），从里面找出 `token`、`refresh_token`、`device_id` 三个值，存成 `~/.getnote/web_token.json`：
   ```json
   { "token": "eyJ...", "refresh_token": "AAAA...", "device_id": "..." }
   ```
5. `chmod 600 ~/.getnote/web_token.json`

> 踩坑：
> - access `token` 只活 30 分钟，但脚本会用 `refresh_token` 自动续，`refresh_token` 约 3 个月有效，到期再重做本步即可。
> - 如果 `localStorage.getItem("token")` 返回 undefined，多半是页面不对（要在能看到笔记的页面）或键名不同——所以这里用 `JSON.stringify(localStorage)` 整个复制，最稳。

## 第 3 步 · 配置（把"会变的"改成你的）
```bash
cd getnote-to-obsidian
cp config/config.example.yaml     config/config.yaml
cp config/tags.example.yaml       config/tags.yaml
cp config/categories.example.yaml config/categories.yaml
cp config/routing.example.yaml    config/routing.yaml
```
打开 `config/config.yaml`，至少改一处：**`vault:` 指向你的 Obsidian 库**。
其余（标签库 `tags.yaml`、分类 `categories.yaml`、路由 `routing.yaml`）按你的体系改，不改也能先跑。

> 你的 `*.yaml`（含路径）和 `~/.getnote/*.json`（凭据）都已被 `.gitignore`，不会进仓库。

## 第 4 步 · 试跑
```bash
python scripts/gn_sync.py --dry-run     # 只预览，不写任何文件
```
看着没问题，再正式跑（见 README「使用」）。

## 自检清单
- [ ] `~/.getnote/config.json` 存在且 chmod 600
- [ ] `config/config.yaml` 里 `vault` 指对了
- [ ] `--dry-run` 能列出将要归档的笔记
- [ ] （要发芽才需要）`~/.getnote/web_token.json` 存在
