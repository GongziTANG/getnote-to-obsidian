# -*- coding: utf-8 -*-
"""
common.py — 共享层：配置加载、凭据、开放 API、web 内部 API(自动刷新 token)。
所有脚本 import 它，逻辑稳定、个性化在 config/。
"""
import os, re, json, time, base64, pathlib, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"

def _expand(p): return pathlib.Path(os.path.expanduser(str(p)))

def load_yaml(name):
    import yaml  # pip install pyyaml
    f = CONFIG_DIR / name
    if not f.exists():
        f = CONFIG_DIR / name.replace(".yaml", ".example.yaml")
    return yaml.safe_load(f.read_text(encoding="utf-8"))

def cfg():
    c = load_yaml("config.yaml")
    for k in ("vault", "audio_dir", "state_file", "open_api_creds", "web_token_file"):
        if k in c: c[k] = _expand(c[k])
    return c

# ── 开放 API ────────────────────────────────────────────────
OPEN_BASE = "https://openapi.biji.com/open/api/v1/resource"

def open_creds(c):
    d = json.loads(_expand(c["open_api_creds"]).read_text())
    return d["api_key"], d["client_id"]

def open_get(c, path):
    key, cid = open_creds(c)
    req = urllib.request.Request(OPEN_BASE + path, headers={
        "Authorization": f"Bearer {key}", "X-Client-Id": cid, "Accept-Encoding": "identity"})
    return json.loads(urllib.request.urlopen(req, timeout=40).read())

def note_detail(c, nid):
    """raw 详情：含 CLI 丢弃的 audio.original / children_ids。"""
    return open_get(c, f"/note/detail?id={nid}").get("data", {}).get("note", {})

# 官方 CLI (@getnote/cli) —— 用于列表分页与打标签（文档化、稳）
import subprocess, shutil
def cli(c, *args):
    """调用官方 getnote CLI。需 `npm i -g @getnote/cli` 且已 auth login。"""
    binp = c.get("getnote_cli") or shutil.which("getnote") or "getnote"
    p = subprocess.run([binp, "-o", "json", *args], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"getnote {' '.join(args)}: {p.stderr.strip()[:200]}")
    return json.loads(p.stdout) if p.stdout.strip().startswith(("{", "[")) else p.stdout

def list_all_notes(c):
    return cli(c, "notes", "--all").get("data", {}).get("notes", [])

def add_tag(c, nid, tag):
    return cli(c, "tag", "add", str(nid), tag)

# ── web 内部 API（发芽等，自动刷新 token）─────────────────────
WEB_BASE = "https://notes-api.biji.com"

class WebClient:
    def __init__(self, c):
        self.path = _expand(c["web_token_file"]); self.d = json.loads(self.path.read_text())
    def _save(self): self.path.write_text(json.dumps(self.d, ensure_ascii=False)); self.path.chmod(0o600)
    def _exp(self, t):
        try: return json.loads(base64.urlsafe_b64decode(t.split(".")[1] + "==")).get("exp", 0)
        except Exception: return 0
    def refresh(self):
        body = json.dumps({"refresh_token": self.d["refresh_token"]}).encode()
        req = urllib.request.Request(WEB_BASE + "/account/v2/web/user/auth/refresh", data=body,
            method="POST", headers={"Content-Type": "application/json", "X-Appid": "3"})
        r = json.loads(urllib.request.urlopen(req, timeout=20).read()).get("c", {})
        tk = r.get("token"); newtok = tk.get("token") if isinstance(tk, dict) else tk
        if not newtok: raise RuntimeError("web token 刷新失败")
        self.d["token"] = newtok
        for rt in (r.get("refresh_token"), isinstance(tk, dict) and tk.get("refresh_token")):
            if rt: self.d["refresh_token"] = rt; break
        self._save(); return newtok
    def token(self):
        t = self.d.get("token", "")
        return t if t and self._exp(t) - time.time() > 120 else self.refresh()
    def get(self, path, _retry=True):
        req = urllib.request.Request(WEB_BASE + path, headers={
            "Authorization": f"Bearer {self.token()}", "X-Appid": "3", "Accept-Encoding": "identity"})
        try: r = json.loads(urllib.request.urlopen(req, timeout=25).read())
        except urllib.error.HTTPError as e:
            if e.code in (401, 403) and _retry: self.refresh(); return self.get(path, False)
            raise
        if isinstance(r, dict) and r.get("h", {}).get("e") == "LoginRequired" and _retry:
            self.refresh(); return self.get(path, False)
        return r

# ── 工具 ────────────────────────────────────────────────────
def safe_filename(s, maxlen=60):
    s = re.sub(r'[\\/:*?"<>|\n\r\t]', "_", s or "").strip()
    return (re.sub(r"\s+", " ", s)[:maxlen]).rstrip(" ._") or "untitled"

def index_archived(vault):
    """库内已归档 md：getnote_id → path。靠 frontmatter source_type: getnote 标识。"""
    import glob
    idx = {}
    for f in glob.glob(str(vault / "**/*.md"), recursive=True):
        try:
            head = open(f, encoding="utf-8", errors="ignore").read(400)
            if 'source_type: "getnote"' in head:
                m = re.search(r'getnote_id:\s*"(\d+)"', head)
                if m: idx[m.group(1)] = pathlib.Path(f)
        except Exception: pass
    return idx
