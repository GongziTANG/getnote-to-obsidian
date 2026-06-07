#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gn_timedata.py — 从归档 md 聚合某时间段的「时间账」(柳比歇夫式量化)，喂给日/周/月反思。
纯读本地 md，不调 API。用法:
  python scripts/gn_timedata.py --day today
  python scripts/gn_timedata.py --since 2026-06-01 --until 2026-06-07 [--json]"""
import re, glob, json, argparse, datetime, pathlib
import common as C

def parse_minutes(content):
    m = re.search(r"时长[^\n]*", content) or re.search(r"duration[^\n]*", content, re.I)
    if not m: return 0
    line = m.group(0)
    h = re.search(r"(\d+)\s*(?:小时|h)", line); mi = re.search(r"(\d+)\s*(?:分钟|m\b)", line)
    return (int(h.group(1)) if h else 0) * 60 + (int(mi.group(1)) if mi else 0)

def load(vault, since, until):
    rows = []
    for f in glob.glob(str(vault / "**/*.md"), recursive=True):
        try: text = open(f, encoding="utf-8", errors="ignore").read()
        except Exception: continue
        if 'source_type: "getnote"' not in text[:400]: continue
        cre = re.search(r"^created:\s*([\d-]+)", text, re.M)
        if not cre or not (since <= cre.group(1) <= until): continue
        cat = (re.search(r"^category:\s*(\S+)", text, re.M) or [None, "uncategorized"])[1]
        title = (re.search(r'^title:\s*"([^"]*)"', text, re.M) or [None, pathlib.Path(f).stem])[1]
        rows.append({"day": cre.group(1), "category": cat, "title": title, "minutes": parse_minutes(text)})
    return sorted(rows, key=lambda r: r["day"])

def digest(rows, label):
    total = sum(r["minutes"] for r in rows); by = {}
    for r in rows:
        by.setdefault(r["category"], [0, 0]); by[r["category"]][0] += 1; by[r["category"]][1] += r["minutes"]
    L = [f"# 时间账 · {label}", "", f"- 记录 {len(rows)} 条，总时长约 {total//60}h{total%60}m", "", "## 分类分布"]
    for cat, (n, mi) in sorted(by.items(), key=lambda x: -x[1][1]):
        L.append(f"- **{cat}**：{n} 条 · {mi//60}h{mi%60}m")
    L += ["", "## 逐条", "| 日期 | 分类 | 时长(分) | 标题 |", "|---|---|---|---|"]
    for r in rows: L.append(f"| {r['day']} | {r['category']} | {r['minutes']} | {r['title'][:30]} |")
    return "\n".join(L)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day"); ap.add_argument("--since"); ap.add_argument("--until"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args(); c = C.cfg(); vault = c["vault"]; today = datetime.date.today().isoformat()
    if a.day: d = today if a.day == "today" else a.day; since = until = d; label = d
    else: since = a.since or today; until = a.until or today; label = f"{since} ~ {until}"
    rows = load(vault, since, until)
    print(json.dumps({"label": label, "rows": rows}, ensure_ascii=False, indent=2) if a.json else digest(rows, label))

if __name__ == "__main__":
    main()
