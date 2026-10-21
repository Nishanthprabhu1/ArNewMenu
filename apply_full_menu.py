#!/usr/bin/env python3
"""Adds a 'Full Menu' section below the 3D showcase to the Pinocchio menu page.

Usage:  python apply_full_menu.py your-file.html
Creates your-file.full-menu.html (original is left untouched).
"""
import re, sys, pathlib

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "index.html")
html = src.read_text(encoding="utf-8")

def sub_once(pattern, repl, text, regex=False, flags=0):
    new, n = (re.subn(pattern, lambda m: repl, text, count=1, flags=flags)
              if regex else (text.replace(pattern, repl, 1), int(pattern in text)))
    if n == 0:
        sys.exit(f"Could not find anchor: {pattern[:60]!r}")
    return new

# 1. CSS
css = (".menu-heading{position:relative;z-index:2;max-width:1080px;margin:2rem auto 0;padding:0 1rem;"
       "text-align:center;font-family:var(--f-display);font-size:clamp(28px,6vw,44px);font-weight:700;"
       "color:var(--red-900);text-shadow:0 1px 0 rgba(255,255,255,.7)}\n"
       ".menu-heading small{display:block;margin-top:6px;font:600 11px var(--f-sans);letter-spacing:.3em;"
       "text-transform:uppercase;color:var(--red-700)}\n"
       ".showcase{margin-bottom:1rem}\n")
html = sub_once("/* MAIN*/", css + "/* MAIN*/", html)

# 2. Heading before <main>
heading = ('<h2 class="menu-heading" id="menu-heading"><span id="ui-full-menu">Full Menu</span>'
           '<small id="ui-full-menu-sub">All dishes</small></h2>\n')
html = sub_once('<main class="main">', heading + '<main class="main">', html)

# 3. Replace updateCards so cards never fade out
new_update = """function updateCards(vh) {
  document.querySelectorAll('.menu-card').forEach(c => {
    const r = c.parentElement.getBoundingClientRect();
    if (r.bottom < -vh * 0.3 || r.top > vh * 1.3) return;
    const d = clamp(((r.top + r.height / 2) - vh * 0.52) / (vh * 0.5), -1.4, 1.4);
    const ad = Math.abs(d);
    c.style.setProperty('--srx', (d > 0 ? d * 10 : d * 5).toFixed(2) + 'deg');
    c.style.setProperty('--sty', (d > 0 ? d * 24 : 0).toFixed(1) + 'px');
    c.style.setProperty('--sc',  (1 - ad * 0.04).toFixed(3));
    c.style.setProperty('--so',  '1');
  });
}

"""
html = sub_once(r"function updateCards\(vh\) \{.*?\n\}\n\s*(?=function update\(\) \{)", new_update,
                html, regex=True, flags=re.S)

# 4. i18n strings (English + Italian)
html = sub_once("tapReview: 'Tap to review & add notes' },",
                "tapReview: 'Tap to review & add notes',\n        fullMenu: 'Full Menu', fullMenuSub: 'All dishes' },", html)
html = sub_once("tapReview: 'Tocca per rivedere e aggiungere note' },",
                "tapReview: 'Tocca per rivedere e aggiungere note',\n        fullMenu: 'Menu Completo', fullMenuSub: 'Tutti i piatti' },", html)

# 5. applyUIText
html = sub_once(r"\$\('ui-send-wa'\)\.textContent\s*=\s*t\.sendWA;",
                "$('ui-send-wa').textContent       = t.sendWA;\n"
                "  $('ui-full-menu').textContent     = t.fullMenu || 'Full Menu';\n"
                "  $('ui-full-menu-sub').textContent = t.fullMenuSub || 'All dishes';",
                html, regex=True)

# 6. Hide heading if the menu fails to load
html = sub_once("console.error('Menu load error:', err);",
                "console.error('Menu load error:', err);\n    $('menu-heading').style.display = 'none';", html)

out = src.with_name(src.stem + ".full-menu.html")
out.write_text(html, encoding="utf-8")
print("Done ->", out)