# anymetric — Apply Guide

You have 3 files:

```
wire_forms.py    — patches index.html (3 existing forms → Web3Forms)
feedback.html    — standalone /feedback page (also serves as contact)
APPLY.md         — this file
```

---

## Step 1 — Make sure your repo is clean

In VS Code terminal, from project root:

```bash
git status
```

If `index.html` is dirty (from earlier edits today), revert it first:

```bash
git checkout index.html
```

You should see a clean working tree before continuing.

---

## Step 2 — Drop in the files and run the script

Copy `wire_forms.py` and `feedback.html` to your project root (same folder as `index.html`).

Then:

```bash
python wire_forms.py
```

(If `python` isn't found, try `python3` or `py`.)

Expected output:
```
  [ok] wired: audit-intake
  [ok] wired: playbook-download
  [ok] wired: strategy-challenge

[done] All 3 forms wired in index.html
       backup: index.html.bak
```

If anything goes wrong, the script reverts itself. Your `index.html` stays untouched.

---

## Step 3 — Visual sanity check

```bash
git diff index.html
```

You should see exactly **9 added lines** — 3 per form:
- 1 `action="..."` attribute added to each `<form>` tag
- 2 hidden inputs added (`access_key` + `subject`) inside each form

Nothing else should change. If you see anything weird, run `git checkout index.html` and tell me what you saw.

---

## Step 4 — Add the footer link (5 files)

In each of these files, paste this snippet near your existing footer/legal links:

```html
<a href="/feedback">Send feedback</a>
```

Files to update:
- `index.html`
- `results.html`
- `geo-aeo-optimization.html`
- `on-premise-ai.html`
- `white-label.html`

(If you have a shared footer component, just edit that once.)

---

## Step 5 — Test locally before pushing

Open `index.html` in a browser. Easiest way from VS Code:

```bash
# if you have python:
python -m http.server 8000

# or if you have node:
npx serve .
```

Then submit each form with **test data** (use a real email so you can confirm receipt):

| Form | Where | Subject you should receive |
|---|---|---|
| Audit | `index.html` (top section) | `[anymetric] Audit request` |
| Playbook | `index.html` (B08 section) | `[anymetric] Playbook download` |
| Strategy CTA | `index.html` (B09 section) | `[anymetric] Strategy challenge` |
| Feedback | `/feedback.html` | `[anymetric] Contact / feedback` |

**Where the email goes**: by default, Web3Forms sends to the email you used to sign up (looked like `robotixlaws@gmail.com` from the screenshot). If you want it to go to `lab@anymetric.ai` directly:

1. Log into Web3Forms dashboard
2. Forms → Settings → "Send to" → set to `lab@anymetric.ai`
3. Click the verification link they send to that address

Either way the email reaches you, since `lab@anymetric.ai` already forwards to your Gmail via Cloudflare Email Routing. Setting `lab@` as the explicit "send to" is just cleaner for filtering.

---

## Step 6 — Ship it

```bash
git add index.html feedback.html
git commit -m "wire forms to Web3Forms + add /feedback page"
git push
```

Cloudflare Pages auto-deploys in ~30 seconds. Submit one form on the live site to confirm.

---

## Troubleshooting

**Form submits but no email arrives** (after 60 seconds, check spam folder first)

Most likely cause: there's existing JavaScript hijacking form submission to send to Supabase instead.

In VS Code, search the whole project (Ctrl+Shift+F) for:

```
preventDefault
```

If you find a `form.addEventListener('submit', ...)` with `e.preventDefault()` followed by a `fetch()` to Supabase — that's the hijacker. Two options:

1. **Quick fix**: comment out that `addEventListener` block. Forms revert to native HTML submit, which goes to Web3Forms (the `action=` attribute).
2. **Keep both**: change the existing `fetch()` URL to `https://api.web3forms.com/submit` and adjust the body format. (Tell me if you want this — 5 min.)

**Plausible event not firing**

Add `data-analytics="form-submit"` to each form button, then add this once anywhere:

```html
<script>
document.addEventListener('submit', function(e){
  if (window.plausible) window.plausible('form-submit');
});
</script>
```

**Want to revert everything**

```bash
git checkout index.html
rm feedback.html
```

---

## What I tested before shipping these to you

- Script runs cleanly on a fixture matching your file structure: ✅ all 3 forms patched, exactly 9 lines added, zero collateral changes
- Running script twice: ✅ refuses idempotently
- Simulating a failure mid-run: ✅ reverts file back to original state
- `feedback.html`: ✅ parses cleanly, access key embedded once, mobile viewport set, `prefers-reduced-motion` respected, honeypot present, success/error states present

What I could NOT test (because I don't have your repo):
- Whether your existing JS submits forms via fetch to Supabase (see Troubleshooting above)
- Whether your CSP header allows `connect-src https://api.web3forms.com` (browser DevTools → Console will tell you immediately if blocked)
- Whether your footer markup is consistent across the 5 pages (the snippet is generic, should fit any footer)
