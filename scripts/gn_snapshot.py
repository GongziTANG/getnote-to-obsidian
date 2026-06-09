#!/usr/bin/env python3
"""
gn_snapshot.py —— 给知识库做可回退的 git 快照（底线思维：一切可回退）。

为什么单独成 Python 脚本，而不在 bash 里直接调 git：
  在 launchd / systemd 等无人值守上下文，系统 git 访问受保护目录（如 macOS 的
  ~/Downloads，受 TCC 管控）可能被拒：`Operation not permitted`。但若你的 Python
  解释器已获「完全磁盘访问」，由 Python 用 subprocess 发起 git，git 作为子进程借到
  Python 的责任进程授权即可访问。这样无需给 git 单独授权，也无需手动操作。

用法:
  python3 gn_snapshot.py <vault_path> [label]
  # vault_path 也可用环境变量 LIFEOS_VAULT 指定

建议库里的 .gitignore 只版本化文本（md / yaml / 配置），排除音频、图片、视频等二进制，
让快照轻量、专注于「后悔药」用途。无改动时静默通过。
"""
import os
import sys
import subprocess
import datetime


def git(vault, *args):
    return subprocess.run(
        ["git", "-C", vault, *args],
        capture_output=True, text=True,
    )


def main():
    args = sys.argv[1:]
    vault = None
    label = "archive"

    if args and os.path.isdir(args[0]):
        vault = args[0]
        args = args[1:]
    vault = vault or os.environ.get("LIFEOS_VAULT")
    if args:
        label = args[0]

    if not vault:
        print("用法: gn_snapshot.py <vault_path> [label]  (或设 LIFEOS_VAULT 环境变量)")
        return 2

    r = git(vault, "add", "-A")
    if r.returncode != 0:
        print(f"❌ git add 失败: {r.stderr.strip()[:200]}")
        return 1

    msg = f"[auto] {label} snapshot " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    r = git(vault, "commit", "-q", "-m", msg)
    if r.returncode == 0:
        print(f"✅ committed: {msg}")
    else:
        # 无改动时 commit 返回非 0，属正常
        print(f"· nothing to commit (ok): {(r.stdout + r.stderr).strip()[:160]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
