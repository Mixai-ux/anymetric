#!/usr/bin/env python3
"""Fix the same JS bug in the other 4 HTML files. Run from project root."""
import re, shutil
from pathlib import Path

FILES = ["results.html", "geo-aeo-optimization.html", "on-premise-ai.html", "white-label.html"]

NEW_BLOCK = '''document.querySelectorAll("form[name]").forEach(form => {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = form.querySelector("button[type=submit]");
    const originalText = btn ? btn.textContent : "";
    if (btn) { btn.disabled = true; btn.textContent = "SENDING…"; }

    const fd = new FormData(form);
    fd.append("form_source", form.getAttribute("name"));
    fd.append("submitted_at", new Date().toISOString());
    fd.append("page", window.location.pathname);

    try {
      const res = await fetch(FORM_ENDPOINT, {
        method: "POST",
        body: fd
      });
      if (!res.ok) throw new Error("Submit failed: " + res.status);

      if (typeof plausible === "function") {
        plausible("Form Submit Success", { props: { form: form.getAttribute("name") } });
      }
      form.innerHTML = `<div style="padding:40px 0;text-align:center;">
        <div style="font-size:32px;margin-bottom:16px;">✓</div>
        <div style="font-size:18px;font-weight:700;margin-bottom:8px;">Got it. A senior AI PM will respond within 48 hours.</div>
        <div style="font-size:13px;color:var(--text-muted);">Check your inbox — including spam, just in case.</div>
      </div>`;
    } catch (err) {
      console.error(err);
      if (btn) { btn.disabled = false; btn.textContent = originalText; }
      alert("Something went wrong. Please try again or email lab@anymetric.ai");
    }
  });
});
</script>'''

pattern = re.compile(
    r'document\.querySelectorAll\("form\[name\]"\)\.forEach\(form => \{.*?\}\);\r?\n</script>',
    re.DOTALL
)

for name in FILES:
    p = Path(name)
    if not p.exists(): print(f"skip: {name}"); continue
    text = p.read_text(encoding="utf-8", newline="")
    if not pattern.search(text):
        print(f"skip: {name} (JS pattern not found — already fixed?)")
        continue
    shutil.copy(p, p.with_name(p.name + ".bak"))
    new = pattern.sub(NEW_BLOCK.replace("\n", "\r\n"), text, count=1)
    new = new.replace("hello@anymetric.ai", "lab@anymetric.ai")
    p.write_text(new, encoding="utf-8", newline="")
    print(f"[ok] {name}")

print("\nDone. Now:")
print("  Remove-Item *.bak")
print("  git add -A")
print("  git commit -m 'fix forms across all pages'")
print("  git push")
