# anymetric.ai

Production site for [anymetric.ai](https://anymetric.ai) — AI product revenue consultancy.

## Stack
- **Host**: Cloudflare Pages (auto-deploy from this repo)
- **Backend**: Supabase (forms, leads)
- **Analytics**: Plausible + Microsoft Clarity
- **Domain**: Spaceship → Cloudflare DNS

## File Structure
```
index.html                  → anymetric.ai/
geo-aeo-optimization.html   → anymetric.ai/geo-aeo-optimization
on-premise-ai.html          → anymetric.ai/on-premise-ai
results.html                → anymetric.ai/results
white-label.html            → anymetric.ai/white-label
robots.txt                  → Disallow: / during testing, flip to Allow: / at launch
sitemap.xml                 → submit to Google Search Console after go-live
_headers                    → Cloudflare security headers (HSTS, CSP, XSS, etc.)
_redirects                  → clean URL fallbacks
supabase-schema.sql         → paste into Supabase SQL Editor to create leads table
images/                     → og-image.png (1200×630px) + logo.svg MISSING — add these
```

## Accent color & CSS variables
- Design tokens live in `:root` at the top of each HTML file's `<style>` block.
- Accent color is controlled by three CSS variables: `--accent`, `--accent-dim`, `--accent-glow` (plus `--on-accent` for text on accent backgrounds).
- Current accent: amber (`#ffb94c` base, `#e8a020` hover, `rgba(255,185,76,0.12)` glow). The user-facing gradient runs `#ffb94c → #ffe0a0 → #e07020`.
- To A/B test a different accent, update the four variables in each file's `:root` + the gradient stops in `.grad`, `.stat-num`, `.m-num`, and the nav/footer logo `<linearGradient>` definitions. Search for the hex values directly — the variables don't cover the SVG gradient stops or the animated text gradients.

## Before Going Live Checklist

### Must do (site is broken without these)
- [ ] **Add `images/og-image.png`** (1200×630px) — else LinkedIn/Twitter previews empty. *Note: HTML currently references `/og-image.png` (root), not `/images/og-image.png`. Place the file at the repo root, not inside `/images/`.*
- [ ] **Add `logo.svg`** at root — referenced in JSON-LD schema.
- [ ] **Configure Microsoft Clarity**: create account at clarity.microsoft.com, replace `CLARITY_PROJECT_ID` in every HTML file (5 files).
- [ ] **Wire forms to Supabase**:
  1. Run `supabase-schema.sql` in Supabase SQL Editor
  2. In every HTML file, find `UNIVERSAL FORM HANDLER` script at bottom
  3. Set `FORM_ENDPOINT` to `https://YOUR-PROJECT.supabase.co/rest/v1/leads`
  4. Uncomment headers block, paste your Supabase anon key

### Just before launch
- [ ] Flip `robots.txt` line 2 from `Disallow: /` → `Allow: /`
- [ ] Bump `lastmod` dates in `sitemap.xml` to launch date
- [ ] Test all nav links on live `.pages.dev` URL
- [ ] Test form submission end-to-end → lead appears in Supabase table
- [ ] Paste URL into LinkedIn Post Inspector — verify OG image renders
- [ ] Submit `sitemap.xml` to Google Search Console

## Deploying to Cloudflare Pages

1. Push this folder to a GitHub repo
2. cloudflare.com → Pages → Connect to Git → select repo
3. Build settings: framework preset "None", build command empty, output directory `/`
4. Deploy → you get a `xyz.pages.dev` URL
5. Test there first
6. Add custom domain (anymetric.ai) in Pages dashboard — DNS auto-configures

## Changelog

### April 2026 — Launch sprint
- **Footer unified across all 5 pages.** Service pages previously had a stripped-down one-line `.foot-strip`; they now use the same 4-column `<footer>` + legal modal as index.html.
- **Legal modal ported to all subpages.** Privacy Policy, Terms of Service, and Cookie Policy are now reachable from every page footer.
- **Cookie Policy rewritten.** Removed stale Netlify reference; added accurate disclosure that Microsoft Clarity sets functional cookies. Supabase described as form backend (no cookies set by form POSTs).
- **CSS variable rename**: `--amber` → `--accent`, `--amber-dim` → `--accent-dim`, `--amber-glow` → `--accent-glow`, `--on-amber` → `--on-accent`. Pure refactor, no visual change — prepares site for future A/B colour tests without hunting through 5 files.
- **Twitter cards completed** on geo-aeo-optimization, on-premise-ai, and white-label pages (previously had `twitter:card` only, missing title/description/image).
- **Dead form actions removed.** All forms previously had `action="/thank-you"` or `action="/playbook-sent"` pointing at non-existent pages; stripped since the universal JS handler intercepts submits anyway.
- **Content-Security-Policy added to `_headers`.** Covers Plausible, Clarity, Google Fonts, Supabase origins. Includes extension comments for future widgets/pixels.

### Earlier April 2026 sweep
- Removed `data-netlify="true"` from 7 forms (was broken on Cloudflare Pages)
- Added universal form handler ready for Supabase or Formspree
- Added Microsoft Clarity stub to all 5 files
- Updated all `2025` → `2026` references (copyright, legal, FAQ)
- Renamed files to match nav hrefs (geo-aeo-optimization.html, etc.)
- Added Cloudflare `_headers` and `_redirects`
