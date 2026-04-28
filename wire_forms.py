#!/usr/bin/env python3
"""
Wire the 3 anymetric.ai forms in index.html to Web3Forms.

Run from the project root (where index.html lives):
    python wire_forms.py

Behavior:
- Backs up index.html -> index.html.bak first.
- Refuses to run if forms are already wired (idempotent).
- Patches all 3 forms in a single pass, with sanity checks.
- Reverts the file on any failure.
"""

import re
import shutil
import sys
from pathlib import Path

ACCESS_KEY = "0ccc9df0-0528-4fe9-81dd-a593fadfadf3"
INDEX = Path("index.html")

FORMS = [
    ("audit-intake", "[anymetric] Audit request"),
    ("playbook-download", "[anymetric] Playbook download"),
    ("strategy-challenge", "[anymetric] Strategy challenge"),
]


def main() -> None:
    if not INDEX.exists():
        sys.exit("[!] index.html not found. Run this script from the project root.")

    # Read preserving line endings (matters for Windows / git diff cleanliness)
    with open(INDEX, "r", encoding="utf-8", newline="") as f:
        original = f.read()

    if ACCESS_KEY in original:
        sys.exit(
            "[!] Already wired (found access_key in file). Aborting.\n"
            "    To re-run cleanly:  git checkout index.html"
        )

    # Backup
    backup = INDEX.with_name(INDEX.name + ".bak")
    shutil.copy(INDEX, backup)

    html = original
    initial_form_count = original.count("<form ")

    for form_name, subject in FORMS:
        # Step 1: append action="..." to the <form ... name="<form_name>" method="POST"> tag
        form_re = re.compile(
            r'(<form\b[^>]*\bname=)"' + re.escape(form_name) + r'"([^>]*method="POST")(>)',
            re.IGNORECASE,
        )
        new_html, n1 = form_re.subn(
            r'\1"' + form_name + r'"\2 action="https://api.web3forms.com/submit"\3',
            html,
            count=1,
        )
        if n1 != 1:
            _revert(original, f"Could not find <form> tag for '{form_name}'.")
        html = new_html

        # Step 2: inject 2 hidden inputs after the existing form-name hidden input,
        #         re-using its leading whitespace so indentation matches.
        hidden_re = re.compile(
            r'(\s*)(<input\s+type="hidden"\s+name="form-name"\s+value=)"'
            + re.escape(form_name)
            + r'"(\s*>)',
            re.IGNORECASE,
        )
        replacement = (
            r'\1\2"' + form_name + r'"\3'
            r'\1<input type="hidden" name="access_key" value="' + ACCESS_KEY + r'">'
            r'\1<input type="hidden" name="subject" value="' + subject + r'">'
        )
        new_html, n2 = hidden_re.subn(replacement, html, count=1)
        if n2 != 1:
            _revert(original, f"Could not find form-name hidden input for '{form_name}'.")
        html = new_html

        print(f"  [ok] wired: {form_name}")

    # Post-conditions
    if html.count(ACCESS_KEY) != 3:
        _revert(original, f"Expected 3 access_key entries, got {html.count(ACCESS_KEY)}.")

    if html.count("<form ") != initial_form_count:
        _revert(
            original,
            f"<form> tag count changed (was {initial_form_count}, now {html.count('<form ')}). "
            "This means a duplicate was created.",
        )

    # Write
    with open(INDEX, "w", encoding="utf-8", newline="") as f:
        f.write(html)

    print(f"\n[done] All 3 forms wired in {INDEX}")
    print(f"       backup: {backup}")
    print("\nNext steps:")
    print("  1) git diff index.html       # visual sanity check (expect 9 added lines: 3 per form)")
    print("  2) Open index.html locally, submit a form, check Web3Forms dashboard")
    print("  3) git add index.html && git commit -m 'wire forms to web3forms' && git push")


def _revert(original: str, msg: str) -> None:
    with open(INDEX, "w", encoding="utf-8", newline="") as f:
        f.write(original)
    sys.exit(f"[!] {msg}\n    Reverted index.html to original state.")


if __name__ == "__main__":
    main()
