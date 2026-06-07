#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gn_sync.py — Get笔记 → Obsidian 归档(暂存到 inbox_subdir)。配置驱动、幂等、单向只增不改。
列表/打标签用官方 CLI；详情用 raw API。用法:
  python scripts/gn_sync.py [--dry-run] [--limit N] [--no-audio] [--no-tag]"""
import argparse, json, urllib.request, urllib.parse, pathlib
import common as C

def classify(title, content, ai_tags, cats):
    for key, v in cats["categories"].items():
        if any(k in (title or "") for k in v["keywords"]): return key
    hay = f"{content or ''} {' '.join(ai_tags or [])}"
    for key, v in cats["categories"].items():
        if any(k in hay for k in v["keywords"]): return key
    return cats.get("fallback", "uncategorized")

def yl(items): return "[" + ", ".join(f'"{i}"' for i in items) + "]"

def dl_audio(url, dest):
    host = urllib.parse.urlparse(url).hostname or ""
    if not (host.endswith("umiwi.com") or host.endswith("biji.com")): return None
    if dest.exists() and dest.stat().st_size > 0: return dest.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "gn/1.0"}), timeout=60) as r, open(dest, "wb") as f:
            while (b := r.read(65536)): f.write(b)
        return dest.name
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--no-audio", action="store_true"); ap.add_argument("--no-tag", action="store_true")
    a = ap.parse_args()
    c = C.cfg(); cats = C.load_yaml("categories.yaml"); tags = C.load_yaml("tags.yaml")
    inbox = c["vault"] / c["inbox_subdir"]; audio_dir = c["audio_dir"]; tag = c.get("archive_tag", "ArchivedToObsidian")
    state_f = c["state_file"]; state = json.loads(state_f.read_text()) if state_f.exists() else {"archived_ids": []}
    archived = set(state["archived_ids"])

    notes = C.list_all_notes(c)
    notes.sort(key=lambda n: n.get("created_at") or "", reverse=True)
    if a.limit: notes = notes[:a.limit]
    if not a.dry_run: inbox.mkdir(parents=True, exist_ok=True)
    done = skip = 0
    for n in notes:
        nid = str(n.get("note_id") or n.get("id"))
        if nid in archived or any(t.get("name") == tag for t in n.get("tags", []) or []):
            skip += 1; continue
        d = C.note_detail(c, nid)
        title = d.get("title") or "untitled"; content = d.get("content") or ""; created = d.get("created_at") or ""
        ai = [t["name"] for t in d.get("tags", []) if isinstance(t, dict) and t.get("type") != "system"]
        cat = classify(title, content, ai, cats)
        btags = list(tags.get("baseline", [])) + [f"cat/{cat}"]
        gtags = ai if tags.get("keep_original_ai_tags", True) else []
        audio_url = next((x.get("url") for x in d.get("attachments", []) or [] if isinstance(x, dict) and x.get("type") == "audio"), "")
        stem = f"{(created or '')[:10] or 'nodate'}__{C.safe_filename(title)}__{nid[-6:]}"
        alocal = dl_audio(audio_url, audio_dir / (stem + ".mp3")) if (audio_url and not a.no_audio and not a.dry_run) else None
        fm = ["---", 'source: "Get笔记"', 'source_type: "getnote"', f'getnote_id: "{nid}"',
              f'title: "{title.replace(chr(34), chr(39))}"', f"created: {created}", 'status: "raw"',
              f"tags: {yl(btags)}", f"getnote_tags: {yl(gtags)}", f"category: {cat}"]
        if audio_url: fm.append(f'audio_url: "{audio_url}"')
        if alocal: fm.append(f'audio_local: "{alocal}"')
        fm += ["---", "", f"# {title}", "", content.strip(), "",
               "\n---\n## 🪡 创作工作区", "- 钩子：", "- 选题：", "- 平台：" + "、".join(c.get("platforms", [])), ""]
        if a.dry_run:
            print(f"[DRY] {cat:12} {stem}.md"); done += 1; continue
        (inbox / (stem + ".md")).write_text("\n".join(fm), encoding="utf-8")
        if not a.no_tag:
            try: C.add_tag(c, nid, tag)
            except Exception as e: print(f"  ⚠ 打标签失败 {nid}: {e}")
        archived.add(nid); done += 1; print(f"✅ {cat:12} {stem}.md")
    if not a.dry_run:
        state["archived_ids"] = sorted(archived); state_f.parent.mkdir(parents=True, exist_ok=True)
        state_f.write_text(json.dumps(state, ensure_ascii=False, indent=2))
    print(f"完成：新归档 {done} · 跳过 {skip}")

if __name__ == "__main__":
    main()
