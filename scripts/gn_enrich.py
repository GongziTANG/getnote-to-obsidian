#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gn_enrich.py — 抓「追加笔记」(children_ids 子笔记)插入归档 md【创作工作区后、录音原文前】。
幂等。用法: python scripts/gn_enrich.py [--limit N]"""
import argparse
import common as C

MARK = "## ➕ 追加笔记"
ANCHOR = "\n\n---\n## 🎙️ 录音原文"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args(); c = C.cfg(); idx = C.index_archived(c["vault"])
    ids = sorted(idx)[: a.limit or None]
    done = skip = none = 0
    for nid in ids:
        md = idx[nid]; text = md.read_text(encoding="utf-8", errors="ignore")
        if MARK in text: skip += 1; continue
        d = C.note_detail(c, nid); children = d.get("children_ids") or []
        if not children: none += 1; continue
        parts = [f"\n\n---\n{MARK}", "> 源笔记的追加子笔记。", ""]
        for ch in children:
            cd = C.note_detail(c, ch)
            parts.append(f"### {cd.get('title') or '追加'}（{cd.get('created_at','')}）")
            parts.append((cd.get("content") or "").strip()); parts.append("")
        block = "\n".join(parts)
        pos = text.find(ANCHOR)
        text = (text[:pos] + block + text[pos:]) if pos != -1 else text.rstrip() + "\n" + block + "\n"
        md.write_text(text, encoding="utf-8"); done += 1; print(f"✅ {md.name[:40]} ← {len(children)}条追加")
    print(f"完成：补追加 {done} · 已有 {skip} · 无追加 {none}")

if __name__ == "__main__":
    main()
