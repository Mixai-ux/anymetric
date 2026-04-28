#!/usr/bin/env python3
"""Run from project root: python fix_fetch.py"""
import re, shutil
from pathlib import Path

FILES = ["index.html","results.html","geo-aeo-optimization.html","on-premise-ai.html","white-label.html"]

# Fix 1: Switch from JSON to FormData in the fetch call
# Old pattern (JSON approach)
OLD_FETCH = '''      const data = Object.fromEntries(new FormData(form));
      data.form_source = form.getAttribute("name");
      data.submitted_at = new Date().toISOString();
      data.page = window.location.pathname;'''

NEW_FETCH = '''      const fd = new FormData(form);
      fd.append("form_source", form.getAttribute("name"));
      fd.append("submitted_at", new Date().toISOString());
      fd.append("page", window.location.pathname);'''

OLD_BODY = '''        const res = await fetch(FORM_ENDPOINT, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            // Uncomment for Supabase:
            // "apikey": "YOUR_SUPABASE_ANON_KEY",
            // "Authorization": "Bearer YOUR_SUPABASE_ANON_KEY",
            // "Prefer": "return=minimal"
          },
          body: JSON.stringify(data)
        });'''

NEW_BODY = '''        const res = await fetch(FORM_ENDPOINT, {
          method: "POST",
          body: fd
        });'''

# Fix 2: Update CSP in _headers to allow web3forms
HEADERS_FILE = Path("_headers")

def fix_html(path):
    if not path.exists(): print(f"  skip: not found"); return False
    text = path.read_text(encoding="utf-8")
    changed = False

    # Try to replace fetch block
    if OLD_FETCH in text:
        text = text.replace(OLD_FETCH, NEW_FETCH, 1)
        changed = True
        print(f"  [ok] switched to FormData")
    
    if OLD_BODY in text:
        text = text.replace(OLD_BODY, NEW_BODY, 1)
        changed = True
        print(f"  [ok] removed JSON headers")

    # Also replace data. references with fd.append in case spacing differs
    if not changed:
        # Try looser pattern
        text2 = re.sub(
            r'headers:\s*\{[^}]*"Content-Type"\s*:\s*"application/json"[^}]*\},\s*\n\s*body:\s*JSON\.stringify\(data\)',
            'body: fd',
            text, count=1
        )
        if text2 != text:
            text = text2
            changed = True
            print(f"  [ok] removed JSON headers (loose match)")

    if not changed:
        print(f"  [!] pattern not matched — check manually")
        return False

    shutil.copy(path, path.with_name(path.name + ".bak"))
    path.write_text(text, encoding="utf-8")
    return True

def fix_headers():
    if not HEADERS_FILE.exists():
        print("\n_headers: not found — creating with CSP that allows web3forms")
        HEADERS_FILE.write_text(
            "/*\n  Content-Security-Policy: default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://plausible.io https://www.clarity.ms; "
            "connect-src 'self' https://api.web3forms.com https://plausible.io; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:;\n"
        )
        return

    text = HEADERS_FILE.read_text(encoding="utf-8")
    if "api.web3forms.com" in text:
        print("\n_headers: already allows web3forms"); return

    # Add to connect-src if it exists
    if "connect-src" in text:
        text = re.sub(
            r"(connect-src\s+[^\n]+)",
            r"\1 https://api.web3forms.com",
            text, count=1
        )
        print("\n_headers: [ok] added web3forms to connect-src")
    else:
        print("\n_headers: no connect-src found — add manually if you have strict CSP")
        return

    shutil.copy(HEADERS_FILE, Path("_headers.bak"))
    HEADERS_FILE.write_text(text, encoding="utf-8")

print("=== Fixing fetch calls ===")
for name in FILES:
    print(f"\n{name}:")
    fix_html(Path(name))

fix_headers()

print("\n\nDone. Run:")
print("  git rm *.bak 2>nul & git add -A && git commit -m 'fix: use FormData for web3forms' && git push")
