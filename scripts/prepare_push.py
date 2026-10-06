#!/usr/bin/env python3
"""Bagi file repo jadwal-sholat-indonesia menjadi batch JSON untuk push_files.

Tiap batch: {"owner","repo","branch","message","files":[{"path","content"}]}
Target ukuran per batch bisa diatur via MAX_KB (batas argumen CLI).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = "/tmp/jadwal-push"
MAX_KB = float(sys.argv[1]) if len(sys.argv) > 1 else 400

SKIP_DIRS = {"__pycache__", ".git"}
SKIP_FILES = set()

# urutan: file kecil/dokumen dulu, lalu data
def sort_key(rel):
    if rel in ("README.md", "llms.txt", "SUMBER-DATA.md", "LICENSE", ".gitignore"):
        return (0, rel)
    if rel.startswith("examples/") or rel.startswith("scripts/") or rel == "demo.html":
        return (1, rel)
    if rel in ("api/cities.json", "api/index.json", "source/cities.json"):
        return (2, rel)
    return (3, rel)

files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        if fn in SKIP_FILES:
            continue
        full = os.path.join(dirpath, fn)
        rel = os.path.relpath(full, ROOT)
        files.append(rel)
files.sort(key=sort_key)

os.makedirs(OUTDIR, exist_ok=True)
batches, cur, cur_kb = [], [], 0.0
for rel in files:
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        content = f.read()
    kb = len(content.encode("utf-8")) / 1024
    if cur and cur_kb + kb > MAX_KB:
        batches.append(cur)
        cur, cur_kb = [], 0.0
    cur.append({"path": rel, "content": content})
    cur_kb += kb
if cur:
    batches.append(cur)

for i, chunk in enumerate(batches, 1):
    payload = {"owner": "ANGGATYASIA", "repo": "jadwal-sholat-indonesia",
               "branch": "main",
               "message": f"Jadwal sholat Indonesia (batch {i}/{len(batches)})",
               "files": chunk}
    out = os.path.join(OUTDIR, f"batch-{i:03d}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    print(f"{out}: {len(chunk)} files, {os.path.getsize(out)/1024:.0f} KB")

print(f"TOTAL: {len(files)} files dalam {len(batches)} batch")
