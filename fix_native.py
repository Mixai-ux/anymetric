#!/usr/bin/env python3
"""
Bypass JS fetch — let forms POST natively to Web3Forms.
Run from project root: python fix_native.py
"""
import shutil
from pathlib import Path

FILES = ["index.html","results.html","geo-aeo-optimization.html","on-premise-ai.html","white-label.html"]

# At the very start of the submit handler, bail out if form targets web3forms
# so native POST takes over (no CSP issues, no CORS, guaranteed delivery)
OLD = 'form.addEventListener("submit", async (e) => {'
NEW = '''form.addEventListener("submit", async (e) => {
    if (form.action && form.action.includes("web3forms")) return;'''

total = 0
for name in FILES:
    p = Path(name)
    if not p.exists(): print(f"skip: {name}"); continue
    text = p.read_text(encoding="utf-8")
    if "web3forms.com" not in text: print(f"skip: {name} (not wired yet)"); continue
    if 'form.action.includes("web3forms")' in text: print(f"skip: {name} (already patched)"); continue
    count = text.count(OLD)
    if not count: print(f"skip: {name} (pattern not found)"); continue
    shutil.copy(p, p.with_name(p.name + ".bak"))
    p.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print(f"[ok] {name}")
    total += 1

print(f"\nDone. {total} file(s) patched.")
print("\nNow set the thank-you redirect in Web3Forms dashboard:")
print("  Settings → Redirect URL → https://anymetric.ai/thank-you.html")
print("\nThen:")
print("  git rm *.bak")
print("  git add -A")
print("  git commit -m \"fix: native form post to web3forms\"")
print("  git push")
