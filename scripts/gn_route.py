#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gn_route.py — 把 inbox 暂存的归档 md 按 routing.yaml 路由到正确文件夹 + 写溯源日志(+回滚json)。
move 不覆盖；敏感目录只标记进日志请人复核。用法: python scripts/gn_route.py [--dry-run]"""
import argparse, json, glob, re, shutil, datetime, pathlib
import common as C

def route(category, title, content, R):
    hay = f"{title}\n{content}"
    for rule in R.get("by_keyword", []):
        if any(k in hay for k in rule["keywords"]):
            return rule["folder"], bool(rule.get("sensitive"))
    folder = R.get("by_category", {}).get(category) or R.get("staging")
    return folder, False

def parse(p):
    t = p.read_text(encoding="utf-8", errors="ignore")
    g = lambda pat, d="": (re.search(pat, t, re.M) or [None, d])[1]
    return {"category": g(r"^category:\s*(\S+)", "uncategorized"),
            "title": g(r'^title:\s*"([^"]*)"', p.stem),
            "id": g(r'^getnote_id:\s*"(\d+)"'), "body": t}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    c = C.cfg(); R = C.load_yaml("routing.yaml"); vault = c["vault"]
    inbox = vault / c["inbox_subdir"]
    files = sorted(glob.glob(str(inbox / "*.md")))
    rows, moved, skip, sens = [], 0, 0, 0
    for f in files:
        p = pathlib.Path(f); info = parse(p)
        folder, sensitive = route(info["category"], info["title"], info["body"], R)
        dest = (vault / folder / p.name)
        if not str(dest.resolve()).startswith(str(vault.resolve())): continue
        status = "skip(exists)" if dest.exists() else "move"
        if not dest.exists():
            if not a.dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(p), str(dest))
            moved += 1
        else: skip += 1
        if sensitive: sens += 1
        rows.append({"id": info["id"], "title": info["title"], "category": info["category"],
                     "folder": folder, "sensitive": sensitive, "from": p.name, "status": status})
        print(f"{'🔒' if sensitive else '  '} {info['category']:12} → {folder}")
    print(f"移动 {moved} · 跳过 {skip} · 敏感 {sens}")
    if a.dry_run: return
    logdir = vault / c.get("log_subdir", "_Meta/ArchiveLog"); logdir.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    (logdir / f"{today}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    L = [f"# Archive Log {today}", "", f"- moved {moved} · skipped {skip} · sensitive {sens}", "",
         "| title | category | folder | sensitive | status |", "|---|---|---|---|---|"]
    for r in rows: L.append(f"| {r['title'][:28]} | {r['category']} | `{r['folder']}` | {r['sensitive']} | {r['status']} |")
    (logdir / f"{today}-log.md").write_text("\n".join(L), encoding="utf-8")
    print(f"📝 日志: {c.get('log_subdir')}/{today}-log.md")

if __name__ == "__main__":
    main()
