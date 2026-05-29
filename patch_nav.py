#!/usr/bin/env python3
"""
Replace old hamburger/nav-drawer pattern with new burger + side drawer.

Usage:
  python patch_nav.py                 – patch all 15 HTML files
  python patch_nav.py index.html      – patch one file (relative to script dir)
"""
import re, sys, glob, os

ROOT = os.path.dirname(os.path.abspath(__file__))

# ── New CSS injected before </style> ─────────────────────────────────────────
NEW_CSS = """\

/* ═══ SITE-NAV / SIDE DRAWER (replaces .nav-hamburger + .nav-drawer) ═══ */
:root{--accent-glow:rgba(255,185,76,.12);}
nav.site-nav{display:flex;align-items:center;justify-content:space-between;height:64px;padding:0 48px;}
.nav-right{display:flex;align-items:center;gap:20px;}
.burger{display:flex;flex-direction:column;justify-content:center;gap:5px;width:36px;height:36px;background:none;border:none;cursor:pointer;padding:4px;flex-shrink:0;}
.burger span{display:block;height:1.5px;background:var(--text-mid);border-radius:2px;transition:transform .25s ease,opacity .2s ease;}
.burger.open span:nth-child(1){transform:translateY(6.5px) rotate(45deg);}
.burger.open span:nth-child(2){opacity:0;transform:scaleX(0);}
.burger.open span:nth-child(3){transform:translateY(-6.5px) rotate(-45deg);}
.drawer-overlay{position:fixed;inset:0;z-index:300;background:rgba(0,0,0,.5);opacity:0;pointer-events:none;transition:opacity .3s ease;}
.drawer-overlay.open{opacity:1;pointer-events:auto;}
.drawer{position:fixed;top:0;right:0;bottom:0;z-index:301;width:280px;background:var(--navy-mid);border-left:1px solid var(--hairline);display:flex;flex-direction:column;transform:translateX(100%);transition:transform .3s ease;padding:80px 0 40px;}
.drawer.open{transform:translateX(0);}
.drawer-nav{display:flex;flex-direction:column;flex:1;}
.drawer-item{font-size:12px;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--text-muted);text-decoration:none;padding:18px 32px;border-bottom:1px solid var(--hairline);transition:color .2s,background .2s;}
.drawer-item:hover{color:var(--accent);background:var(--accent-glow);}
.drawer-cta{padding:32px;}
.drawer-cta a{display:block;text-align:center;padding:14px 20px;background:var(--accent);color:var(--on-accent);font-weight:700;font-size:11px;letter-spacing:.14em;text-transform:uppercase;text-decoration:none;transition:background .2s;}
.drawer-cta a:hover{background:var(--accent-dim);}
@media(max-width:768px){nav.site-nav{padding:0 20px !important;}}
@media(max-width:480px){nav.site-nav{padding:0 16px !important;}}
"""

# ── New JS replacing the old ham/closeDrawer section ─────────────────────────
NEW_JS = (
    "// Burger / side drawer\n"
    "const burger=document.getElementById('burger');\n"
    "const drawer=document.getElementById('drawer');\n"
    "const overlay=document.getElementById('drawerOverlay');\n"
    "function openDrawer(){drawer.classList.add('open');overlay.classList.add('open');burger.classList.add('open');"
    "burger.setAttribute('aria-expanded','true');drawer.setAttribute('aria-hidden','false');"
    "document.body.style.overflow='hidden';}\n"
    "function closeDrawer(){drawer.classList.remove('open');overlay.classList.remove('open');burger.classList.remove('open');"
    "burger.setAttribute('aria-expanded','false');drawer.setAttribute('aria-hidden','true');"
    "document.body.style.overflow='';}\n"
    "burger.addEventListener('click',()=>drawer.classList.contains('open')?closeDrawer():openDrawer());\n"
    "overlay.addEventListener('click',closeDrawer);\n"
    "document.addEventListener('keydown',e=>{if(e.key==='Escape')closeDrawer();});\n"
    "window.addEventListener('scroll',()=>{if(drawer.classList.contains('open'))closeDrawer();},{passive:true});"
)

# ── Drawer HTML per locale ────────────────────────────────────────────────────
DRAWER_DATA = {
    'en': {
        'items': [
            ('/',                      'Home'),
            ('/results',               'Results'),
            ('/geo-aeo-optimization',  'GEO / AEO Optimization'),
            ('/on-premise-ai',         'On-Premise AI'),
            ('/white-label',           'White Label'),
        ],
        'cta_href':  '/#audit',
        'cta_label': 'GET A FREE AUDIT →',
    },
    'de': {
        'items': [
            ('/de/',                        'Startseite'),
            ('/de/results',                 'Ergebnisse'),
            ('/de/geo-aeo-optimization',    'GEO / AEO-Optimierung'),
            ('/de/on-premise-ai',           'On-Premise-KI'),
            ('/de/white-label',             'White Label'),
        ],
        'cta_href':  '/de/#audit',
        'cta_label': 'Kostenloses Audit →',
    },
    'ru': {
        'items': [
            ('/ru/',                       'Главная'),
            ('/ru/results',                'Результаты'),
            ('/ru/geo-aeo-optimization',   'GEO / AEO Оптимизация'),
            ('/ru/on-premise-ai',          'On-Premise ИИ'),
            ('/ru/white-label',            'White Label'),
        ],
        'cta_href':  '/ru/#audit',
        'cta_label': 'Бесплатный аудит →',
    },
}

def build_drawer_html(locale):
    d = DRAWER_DATA[locale]
    items_html = '\n    '.join(
        f'<a class="drawer-item" href="{href}">{label}</a>'
        for href, label in d['items']
    )
    return (
        '<!-- DRAWER OVERLAY -->\n'
        '<div class="drawer-overlay" id="drawerOverlay"></div>\n'
        '\n'
        '<!-- DRAWER -->\n'
        '<aside class="drawer" id="drawer" aria-hidden="true">\n'
        '  <nav class="drawer-nav">\n'
        f'    {items_html}\n'
        '  </nav>\n'
        '  <div class="drawer-cta">\n'
        f'    <a href="{d["cta_href"]}">{d["cta_label"]}</a>\n'
        '  </div>\n'
        '</aside>'
    )

def get_locale(path):
    p = path.replace('\\', '/')
    if '/de/' in p: return 'de'
    if '/ru/' in p: return 'ru'
    return 'en'

def patch_file(path):
    html = open(path, encoding='utf-8').read()
    orig = html
    locale = get_locale(path)

    # ── 1. Extract logo + lang-switcher from existing nav ─────────────────────
    nav_m = re.search(r'<nav\b[^>]*>([\s\S]*?)</nav>', html)
    if not nav_m:
        print(f'  SKIP  (no <nav>): {path}')
        return

    nav_inner = nav_m.group(1)

    # logo: <a class="nav-logo" ...>...</a>  (SVG has no </a> inside)
    logo_m = re.search(r'<a class="nav-logo"[\s\S]*?</a>', nav_inner)
    logo_html = logo_m.group(0).strip() if logo_m else \
        '<a class="nav-logo" href="/"><span class="nav-wordmark">anymetric</span></a>'

    # lang switcher: <details class="lang-sw" ...>...</details>
    sw_m = re.search(r'<details class="lang-sw"[\s\S]*?</details>', nav_inner)
    sw_html = sw_m.group(0).strip() if sw_m else ''

    # ── 2. Build new nav HTML ─────────────────────────────────────────────────
    sw_block = f'\n    {sw_html}' if sw_html else ''
    new_nav = (
        '<!-- NAV -->\n'
        '<nav class="site-nav">\n'
        f'  {logo_html}\n'
        '  <div class="nav-right">'
        f'{sw_block}\n'
        '    <button class="burger" id="burger" aria-label="Toggle navigation" aria-expanded="false">\n'
        '      <span></span><span></span><span></span>\n'
        '    </button>\n'
        '  </div>\n'
        '</nav>'
    )

    # Replace the first <nav>...</nav> block (with optional preceding <!-- NAV --> comment)
    html = re.sub(
        r'(?:<!-- NAV -->\s*\n)?<nav\b[^>]*>[\s\S]*?</nav>',
        new_nav, html, count=1
    )

    # ── 3. Replace old drawer div ─────────────────────────────────────────────
    # Covers:  <!-- Mobile nav drawer -->\n<div class="nav-drawer"…>…</div>
    # and:     <div class="nav-drawer"…>…</div>  (no comment)
    drawer_replaced = [False]
    def replace_drawer(m):
        drawer_replaced[0] = True
        return build_drawer_html(locale)

    html = re.sub(
        r'(?:<!-- Mobile nav drawer -->[ \t]*\n)?<div class="nav-drawer"[\s\S]*?</div>',
        replace_drawer, html, count=1
    )
    if not drawer_replaced[0]:
        print(f'  WARN  (no nav-drawer div found): {path}')

    # ── 4. Inject new CSS before </style> ─────────────────────────────────────
    html = html.replace('</style>', NEW_CSS + '</style>', 1)

    # ── 5. Replace old hamburger JS ───────────────────────────────────────────
    js_pattern = (
        r'(?:// Mobile nav hamburger[ \t]*\n)?'
        r'const ham=document\.getElementById\(\'navHam\'\);'
        r'[\s\S]*?'
        r"window\.addEventListener\('scroll',[\s\S]*?\{passive:true\}\);"
    )
    new_html, n = re.subn(js_pattern, NEW_JS, html, count=1)
    if n == 0:
        print(f'  WARN  (hamburger JS not matched): {path}')
    else:
        html = new_html

    # ── Write if changed ──────────────────────────────────────────────────────
    if html == orig:
        print(f'  UNCHANGED: {path}')
        return

    open(path, 'w', encoding='utf-8').write(html)
    print(f'  PATCHED:   {path}')

# ── Entry point ───────────────────────────────────────────────────────────────
if len(sys.argv) > 1:
    targets = [os.path.join(ROOT, a) for a in sys.argv[1:]]
else:
    targets = sorted(
        f for f in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)
        if 'nav-hamburger' in open(f, encoding='utf-8').read()
        and 'site-nav' not in open(f, encoding='utf-8').read()
    )

print(f'Patching {len(targets)} file(s)...')
for path in targets:
    patch_file(path)
print('Done.')
