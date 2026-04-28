#!/usr/bin/env python3
"""Run from project root: python fix_redirect.py"""
import shutil
from pathlib import Path

FILES = ["index.html","results.html","geo-aeo-optimization.html","on-premise-ai.html","white-label.html"]
OLD = 'name="access_key" value="0ccc9df0-0528-4fe9-81dd-a593fadfadf3">'
NEW = 'name="access_key" value="0ccc9df0-0528-4fe9-81dd-a593fadfadf3">\n        <input type="hidden" name="redirect" value="false">'

total = 0
for name in FILES:
    p = Path(name)
    if not p.exists(): print(f"skip: {name}"); continue
    text = p.read_text(encoding="utf-8")
    count = text.count(OLD)
    if not count: print(f"skip: {name} (pattern not found)"); continue
    shutil.copy(p, p.with_suffix(p.suffix + ".bak"))
    p.write_text(text.replace(OLD, NEW), encoding="utf-8")
    print(f"[ok] {name} — {count} form(s) fixed")
    total += count

print(f"\nDone. {total} forms updated.")
print("git rm *.bak && git add -A && git commit -m 'fix web3forms redirect' && git push")
