#!/usr/bin/env python3
"""
Fix anymetric.ai forms — Run from project root: python fix_endpoint.py

What it does:
  1. Sets FORM_ENDPOINT = "https://api.web3forms.com/submit" in all 5 HTML files
  2. Adds access_key + subject hidden inputs to forms that don't have them yet
  3. Backs up each file before touching it
"""
import re, shutil
from pathlib import Path

ACCESS_KEY = "0ccc9df0-0528-4fe9-81dd-a593fadfadf3"
ENDPOINT   = "https://api.web3forms.com/submit"

SUBJECTS = {
    "audit-intake":       "[anymetric] Audit request",
    "playbook-download":  "[anymetric] Playbook download",
    "strategy-challenge": "[anymetric] Strategy challenge",
}

FILES = [
    "index.html",
    "results.html",
    "geo-aeo-optimization.html",
    "on-premise-ai.html",
    "white-label.html",
]


def fix(path: Path) -> bool:
    if not path.exists():
        print(f"  [skip] file not found")
        return False

    with open(path, "r", encoding="utf-8", newline="") as f:
        original = f.read()

    html = original
    log  = []

    # ── Step 1: set FORM_ENDPOINT ──────────────────────────────────────────
    needle = 'const FORM_ENDPOINT = "";'
    if needle in html:
        html = html.replace(needle, f'const FORM_ENDPOINT = "{ENDPOINT}";', 1)
        log.append("FORM_ENDPOINT → set")
    elif ENDPOINT in html:
        log.append("FORM_ENDPOINT → already set")
    else:
        print(f"  [!] FORM_ENDPOINT pattern not found — skip")
        return False

    # ── Step 2: add access_key + subject to forms missing them ─────────────
    if ACCESS_KEY in html:
        log.append("access_key → already present, skipped")
    else:
        pattern = re.compile(
            r'(\s+)(<input\s+type="hidden"\s+name="form-name"\s+value="([^"]+)"\s*>)',
            re.IGNORECASE,
        )

        def inject(m):
            ws   = m.group(1)   # leading whitespace (newline + indent)
            tag  = m.group(2)   # the form-name input tag
            name = m.group(3)   # form name value
            subj = SUBJECTS.get(name, f"[anymetric] {name.replace('-',' ').title()}")
            return (
                ws + tag
                + ws + f'<input type="hidden" name="access_key" value="{ACCESS_KEY}">'
                + ws + f'<input type="hidden" name="subject" value="{subj}">'
            )

        new_html = pattern.sub(inject, html)
        n = new_html.count(f'name="access_key"')
        if n:
            html = new_html
            log.append(f"access_key → added to {n} form(s)")
        else:
            log.append("access_key → no form-name inputs found to inject into")

    # ── Write if changed ───────────────────────────────────────────────────
    if html == original:
        print(f"  no changes needed")
        return False

    shutil.copy(path, path.with_name(path.name + ".bak"))
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(html)
    for msg in log:
        print(f"  [ok] {msg}")
    return True


def main():
    updated = 0
    for name in FILES:
        print(f"\n{name}:")
        if fix(Path(name)):
            updated += 1

    print(f"\n{'─'*45}")
    print(f"Done. {updated} file(s) updated.")
    print()
    print("Next:")
    print("  git diff                       # check changes look right")
    print("  git add -A")
    print("  git commit -m 'fix form endpoint'")
    print("  git push")
    print()
    print("Then submit the audit form on anymetric.ai.")
    print("Email should arrive in lab@anymetric.ai within 30 sec.")
    print("Success message will appear inline (already coded in your JS).")


if __name__ == "__main__":
    main()
