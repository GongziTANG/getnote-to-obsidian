#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gn_transcript.py — 抓官方录音原文(audio.original，说话人+时间轴)追加到归档 md 末尾。
幂等。用法: python scripts/gn_transcript.py [--limit N]"""
import argparse
import common as C

MARK = "## 🎙️ 录音原文"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args(); c = C.cfg(); idx = C.index_archived(c["vault"])
    ids = sorted(idx)[: a.limit or None]
    done = skip = empty = 0
    for nid in ids:
        md = idx[nid]; text = md.read_text(encoding="utf-8", errors="ignore")
        if MARK in text: skip += 1; continue
        d = C.note_detail(c, nid); audio = d.get("audio")
        orig = audio.get("original", "") if isinstance(audio, dict) else ""
        if not orig.strip(): empty += 1; continue
        with open(md, "a", encoding="utf-8") as f:
            f.write(f"\n\n---\n{MARK}（说话人·时间轴）\n> Get笔记官方转写 audio.original。\n\n{orig.strip()}\n")
        done += 1; print(f"✅ {len(orig)}字 → {md.name[:40]}")
    print(f"完成：追加 {done} · 已有 {skip} · 无原文 {empty}")

if __name__ == "__main__":
    main()
