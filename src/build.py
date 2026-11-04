#!/usr/bin/env python3
"""Builds the site from src/content.json: English at the root (the App Store
links point there), every other language in its own folder (/de/, /pl/, ...).

Run from the repo root:  python3 src/build.py
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = json.load(open(os.path.join(ROOT, "src", "content.json"), encoding="utf-8"))
ISSUES = "https://github.com/Max-1902/neotracker-site/issues"
LANGS = list(CONTENT)  # English first
PAGES = ["index.html", "privacy.html", "support.html"]


def folder(lang):
    return "" if lang == "en" else f"{lang}/"


def href(from_lang, to_lang, page):
    """Relative link from a page in from_lang's folder to page in to_lang's folder"""
    up = "" if from_lang == "en" else "../"
    target = folder(to_lang) + ("" if page == "index.html" else page)
    return (up + target) or "./"


def paragraphs(text):
    """Plain text with blank-line paragraphs and "- " list items -> HTML"""
    out = []
    for block in text.split("\n\n"):
        lines = block.split("\n")
        if all(line.startswith("- ") for line in lines):
            out.append("<ul>" + "".join(f"<li>{html.escape(l[2:])}</li>" for l in lines) + "</ul>")
        else:
            out.append(f"<p>{html.escape(block)}</p>")
    return "\n".join(out)


def links(t, lang):
    return {"privacy": href(lang, lang, "privacy.html"), "support": href(lang, lang, "support.html"), "issues": ISSUES}


def language_menu(lang, page):
    items = []
    for other in LANGS:
        name = CONTENT[other]["name"]
        current = ' aria-current="true"' if other == lang else ""
        items.append(f'<li><a href="{href(lang, other, page)}" hreflang="{other}" lang="{other}" '
                     f'data-lang="{other}"{current}>{name}</a></li>')
    return (f'<details class="languages"><summary aria-label="{CONTENT[lang]["language"]}">'
            f'<svg aria-hidden="true" viewBox="0 0 24 24" width="18" height="18"><circle cx="12" cy="12" r="9.5" fill="none" stroke="currentColor" stroke-width="1.6"/>'
            f'<path d="M2.5 12h19M12 2.5c2.6 2.8 3.9 6 3.9 9.5s-1.3 6.7-3.9 9.5c-2.6-2.8-3.9-6-3.9-9.5s1.3-6.7 3.9-9.5z" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'
            f'<span>{lang.upper()}</span></summary><ul>{"".join(items)}</ul></details>')


# Root (English) pages send first-time visitors to their browser's language;
# picking a language in the menu is remembered and never overridden
REDIRECT = """<script>
(function () {
  var langs = %s, page = %s, chosen = null;
  try { chosen = localStorage.getItem("lang"); } catch (e) {}
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[data-lang]");
    if (a) { try { localStorage.setItem("lang", a.getAttribute("data-lang")); } catch (err) {} }
  });
  if (chosen) return;
  var wanted = (navigator.languages || [navigator.language || ""]).map(function (l) { return l.slice(0, 2).toLowerCase(); });
  for (var i = 0; i < wanted.length; i++) {
    if (wanted[i] === "en") return;
    if (langs.indexOf(wanted[i]) > 0) { location.replace(wanted[i] + "/" + page); return; }
  }
})();
</script>"""

REMEMBER = """<script>
document.addEventListener("click", function (e) {
  var a = e.target.closest && e.target.closest("a[data-lang]");
  if (a) { try { localStorage.setItem("lang", a.getAttribute("data-lang")); } catch (err) {} }
});
</script>"""


def page(lang, name, title, description, main):
    t = CONTENT[lang]
    up = "" if lang == "en" else "../"
    alternates = "\n".join(f'<link rel="alternate" hreflang="{o}" href="{href(lang, o, name)}">' for o in LANGS)
    script = (REDIRECT % (json.dumps(LANGS), json.dumps("" if name == "index.html" else name))) if lang == "en" else REMEMBER
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="icon" href="{up}icon.png">
<link rel="apple-touch-icon" href="{up}icon.png">
<link rel="stylesheet" href="{up}style.css">
{alternates}
<link rel="alternate" hreflang="x-default" href="{href(lang, 'en', name)}">
{script}
</head>
<body>
<header class="top">
  <a class="brand" href="{href(lang, lang, 'index.html')}"><img src="{up}icon.png" alt="" width="28" height="28"><span>NEO Tracker</span></a>
  <nav>
    <a href="{href(lang, lang, 'privacy.html')}">{t["nav_privacy"]}</a>
    <a href="{href(lang, lang, 'support.html')}">{t["nav_support"]}</a>
    {language_menu(lang, name)}
  </nav>
</header>
<main>
{main}
</main>
<footer>
  <p>{html.escape(t["footer"])}</p>
</footer>
</body>
</html>
"""


def home(lang):
    t = CONTENT[lang]
    up = "" if lang == "en" else "../"
    cards = "\n".join(f'<div class="card"><h2>{html.escape(a)}</h2><p>{html.escape(b)}</p></div>' for a, b in t["cards"])
    return f"""<section class="hero">
<img src="{up}icon.png" alt="" width="112" height="112">
<h1>{t["home_title"]}</h1>
<p class="lead">{html.escape(t["home_lead"])}</p>
</section>
<section class="grid">
{cards}
</section>
<section class="links">
<p><a href="{href(lang, lang, 'privacy.html')}">{t["privacy_title"]}</a> · <a href="{href(lang, lang, 'support.html')}">{t["support_title"]}</a></p>
<p class="meta">{t["no_tracking"]}<br>{t["app_languages"]}</p>
</section>"""


def privacy(lang):
    t = CONTENT[lang]
    sections = [f"<section><h2>{html.escape(title)}</h2>\n{paragraphs(text)}</section>" for title, text in t["privacy_sections"]]
    sections.append(f'<section><h2>{t["website_title"]}</h2>\n<p>{html.escape(t["website_text"])}</p></section>')
    sections.append(f'<section><h2>{t["contact_title"]}</h2>\n<p>{t["contact_text"].format(**links(t, lang))}</p></section>')
    note = f'<p class="note">{html.escape(t["translation_note"])}</p>' if t["translation_note"] else ""
    return f"""<h1>{t["privacy_title"]}</h1>
<p class="lead">{html.escape(t["privacy_intro"])}</p>
<p class="meta">{t["updated"]}</p>
{note}
{chr(10).join(sections)}"""


def support(lang):
    t = CONTENT[lang]
    faq = "\n".join(f"<h3>{html.escape(q)}</h3>\n<p>{a.format(**links(t, lang))}</p>" for q, a in t["faq"])
    return f"""<h1>{t["support_title"]}</h1>
<p class="lead">{html.escape(t["support_lead"])}</p>
<section class="card">
<h2>{t["contact_title"]}</h2>
<p>{t["support_contact"].format(**links(t, lang))}</p>
</section>
<section>
<h2>{t["faq_title"]}</h2>
{faq}
</section>"""


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)


for lang in LANGS:
    t = CONTENT[lang]
    write(folder(lang) + "index.html", page(lang, "index.html", t["home_title"], t["home_description"], home(lang)))
    write(folder(lang) + "privacy.html", page(lang, "privacy.html", f'{t["privacy_title"]} – NEO Tracker', t["privacy_intro"], privacy(lang)))
    write(folder(lang) + "support.html", page(lang, "support.html", f'{t["support_title"]} – NEO Tracker', t["support_lead"], support(lang)))

# Old address of the German privacy policy, given out before the site had language folders
write("datenschutz.html", """<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Datenschutzerklärung – NEO Tracker</title>
<link rel="canonical" href="de/privacy.html"><meta http-equiv="refresh" content="0; url=de/privacy.html"></head>
<body><p><a href="de/privacy.html">Datenschutzerklärung</a></p></body></html>
""")
print("built", len(LANGS), "languages")
