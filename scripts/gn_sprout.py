#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gn_sprout.py — 抓「发芽报告」(web 内部 API，含未存成笔记的)按源笔记精确插入归档 md
【创作工作区后、追加笔记/录音原文前】。需 web token(见 docs/SETUP.md)，自动刷新。
幂等。用法: python scripts/gn_sprout.py [--all] [--ids a,b]"""
import argparse, time
import common as C

MARK = "## 🌱 发芽"
ANCHORS = ["\n\n---\n## ➕ 追加笔记", "\n\n---\n## 🎙️ 录音原文"]

def sprouts(web, nid):
    r = web.get(f"/voicenotes/web/user/sprouts/page_by_note?single_note_id_str={nid}&limit=20")
    out = []
    for t in r.get("c", {}).get("tasks", []) or []:
        out += t.get("sprouts", []) or []
    return out

def full(web, sid):
    r = web.get(f"/voicenotes/web/user/sprout/detail?sprout_id={sid}")
    return (r.get("c", {}).get("sprout") or {}).get("content", "") or ""

def insert(text, block):
    pos = [p for an in ANCHORS if (p := text.find(an)) != -1]
    if pos: i = min(pos); return text[:i] + block + text[i:]
    return text.rstrip() + "\n" + block + "\n"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true"); ap.add_argument("--ids")
    a = ap.parse_args(); c = C.cfg(); web = C.WebClient(c); idx = C.index_archived(c["vault"])
    ids = [x.strip() for x in a.ids.split(",")] if a.ids else (sorted(idx) if a.all else [])
    done = skip = none = 0
    for nid in ids:
        md = idx.get(str(nid))
        if not md: continue
        text = md.read_text(encoding="utf-8", errors="ignore")
        if MARK in text: skip += 1; continue
        sp = sprouts(web, nid)
        if not sp: none += 1; continue
        parts = [f"\n\n---\n{MARK}", "> Get笔记 AI 发芽报告（含未存成笔记的）。", ""]; n = 0
        for s in sp:
            body = full(web, s["id"]).strip() if s.get("id") else ""
            body = body or (s.get("aha", "") or "").strip()
            if not body: continue
            ts = time.strftime("%Y-%m-%d", time.localtime(s["create_time"])) if s.get("create_time") else ""
            parts += [f"### 🌱 {s.get('title','发芽')}（{ts}）", body, ""]; n += 1
        if not n: none += 1; continue
        md.write_text(insert(text, "\n".join(parts)), encoding="utf-8")
        done += 1; print(f"✅ {md.name[:40]} ← {n}条发芽")
    print(f"完成：插入 {done} · 已有 {skip} · 无发芽 {none}")

if __name__ == "__main__":
    main()
