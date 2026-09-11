#!/usr/bin/env python3
"""
Blog-generator voor conti-nu.nl.

Bron:   blog/_bron/<slug>.md   (Markdown met kopregels, zie blog/_bron/LEESMIJ.md)
Uit:    blog/<slug>.html        (artikelpagina)
        blog/index.html         (overzicht, menu "Blog")
        blog/artikelen.json     (machineleesbaar: voor LinkedIn-planner / dashboard)
        blog/feed.xml           (RSS)
        sitemap.xml             (blog-URL's bijgewerkt)

Gebruik:  python3 build_blog.py            # bouwt alles
          python3 build_blog.py --concept  # neemt ook status: concept mee (lokaal nakijken)

Nav, footer en tracking-scripts worden uit over.html geplukt, zodat een
menu-wijziging op de site automatisch in de blog landt. Geen afhankelijkheden
behalve het Python-pakket `markdown`.
"""
import html
import json
import re
import sys
from datetime import datetime, date
from pathlib import Path

try:
    import markdown
except ImportError:  # pragma: no cover
    sys.exit("Installeer eerst: pip3 install markdown")

ROOT = Path(__file__).resolve().parent
BRON = ROOT / "blog" / "_bron"
UIT = ROOT / "blog"
SHELL_PAGE = ROOT / "over.html"
BASE_URL = "https://www.conti-nu.nl"
SITE_NAAM = "CONTI-NU Bedrijfsondersteuning"
STANDAARD_OG = f"{BASE_URL}/Assets/juichende-vrouw-768x422.jpg"

MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni", "juli",
           "augustus", "september", "oktober", "november", "december"]


# ── Bron lezen ────────────────────────────────────────────────────────────
def lees_artikel(pad: Path) -> dict:
    tekst = pad.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", tekst, re.S)
    if not m:
        sys.exit(f"{pad.name}: mist het kopblok tussen '---' regels")
    kop, body = m.group(1), m.group(2)
    meta = {}
    for regel in kop.splitlines():
        if ":" not in regel or regel.lstrip().startswith("#"):
            continue
        k, v = regel.split(":", 1)
        meta[k.strip().lower()] = v.strip().strip('"').strip("'")
    for verplicht in ("titel", "datum", "samenvatting"):
        if not meta.get(verplicht):
            sys.exit(f"{pad.name}: '{verplicht}' ontbreekt in het kopblok")
    try:
        d = date.fromisoformat(meta["datum"])
    except ValueError:
        sys.exit(f"{pad.name}: datum moet als 2026-09-07 geschreven zijn")

    a = {
        "slug": pad.stem,
        "titel": meta["titel"],
        "datum": d,
        "categorie": meta.get("categorie", "Artikel"),
        "samenvatting": meta["samenvatting"],
        "afbeelding": meta.get("afbeelding", ""),
        "afbeelding_alt": meta.get("afbeelding_alt", meta["titel"]),
        "afbeelding_stijl": meta.get("afbeelding_stijl", "foto"),   # foto (vult de kaart) of logo (past erin)
        "auteur": meta.get("auteur", "Dunja Tagliola-Spaan"),
        "status": meta.get("status", "gepubliceerd").lower(),
        "link": meta.get("link", ""),          # extern artikel: kaart linkt daarheen
        "bron": meta.get("bron", ""),           # naam van de externe bron
        "trefwoorden": meta.get("trefwoorden", ""),
        "linkedin": meta.get("linkedin", ""),   # voorstel post-tekst
        "body_md": body.strip(),
    }
    a["url"] = a["link"] or f"{BASE_URL}/blog/{a['slug']}"
    a["pad"] = "" if a["link"] else f"/blog/{a['slug']}"
    if a["afbeelding"]:
        img = a["afbeelding"]
        if not img.startswith(("http://", "https://", "/")):
            img = f"/Assets/blog/{img}"
        a["afbeelding_pad"] = img
        a["afbeelding_url"] = img if img.startswith("http") else BASE_URL + img
    else:
        a["afbeelding_pad"] = a["afbeelding_url"] = ""
    woorden = len(re.findall(r"\w+", body))
    a["leestijd"] = max(1, round(woorden / 200))
    return a


def datum_nl(d: date) -> str:
    return f"{d.day} {MAANDEN[d.month - 1]} {d.year}"


def esc(s: str) -> str:
    return html.escape(s, quote=True)


# ── Site-schil (nav/footer/tracking) uit een bestaande pagina ────────────
def _absoluut(fragment: str) -> str:
    """Relatieve asset-links werken niet vanuit /blog/; maak ze absoluut."""
    fragment = re.sub(r'(href|src)="(Assets/|css/)', r'\1="/\2', fragment)
    fragment = re.sub(r'href="([a-z-]+)\.html(#[^"]*)?"', r'href="/\1\2"', fragment)
    return fragment


def laad_schil() -> dict:
    src = SHELL_PAGE.read_text(encoding="utf-8")
    tracking = re.search(r"(<!-- Google tag.*?</script>\s*<!-- Microsoft Clarity -->.*?</script>)", src, re.S)
    nav = re.search(r"(<!-- ═══ NAV ═══ -->.*?</nav>\s*<nav class=\"mobile-menu\".*?</nav>)", src, re.S)
    staart = re.search(r"(<!-- ═══ FOOTER ═══ -->.*?)</body>", src, re.S)
    if not (tracking and nav and staart):
        sys.exit(f"Kon nav/footer/tracking niet uit {SHELL_PAGE.name} halen")
    navhtml = _absoluut(nav.group(1))
    navhtml = navhtml.replace('class="nav-link active"', 'class="nav-link"')
    navhtml = re.sub(r'(href="/blog"\s*class="nav-link)"', r'\1 active"', navhtml)
    return {"tracking": tracking.group(1), "nav": navhtml, "staart": _absoluut(staart.group(1))}


# ── HTML-bouwstenen ──────────────────────────────────────────────────────
def head(schil, *, titel, beschrijving, url, og_image, og_type="website", extra="", trefwoorden=""):
    kw = f'\n  <meta name="keywords" content="{esc(trefwoorden)}">' if trefwoorden else ""
    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
  {schil['tracking']}
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(titel)} | {SITE_NAAM}</title>
  <meta name="description" content="{esc(beschrijving)}">{kw}
  <link rel="canonical" href="{url}">
  <meta name="robots" content="index, follow">
  <link rel="icon" href="/Assets/favicon.png" type="image/png">
  <link rel="alternate" type="application/rss+xml" title="{SITE_NAAM} blog" href="{BASE_URL}/blog/feed.xml">
  <meta property="og:type"        content="{og_type}">
  <meta property="og:url"         content="{url}">
  <meta property="og:title"       content="{esc(titel)}">
  <meta property="og:description" content="{esc(beschrijving)}">
  <meta property="og:image"       content="{og_image}">
  <meta property="og:site_name"   content="{SITE_NAAM}">
  <meta name="twitter:card"       content="summary_large_image">
{extra}
  <link rel="stylesheet" href="/css/style.css">
</head>
<body>

"""


def kaart(a: dict, vertraging: int) -> str:
    extern = bool(a["link"])
    href = a["link"] if extern else a["pad"]
    target = ' target="_blank" rel="noopener"' if extern else ""
    cta = f"Lees meer bij {esc(a['bron'])}" if extern and a["bron"] else "Lees artikel"
    if a["afbeelding_pad"]:
        beeld = f'<img src="{esc(a["afbeelding_pad"])}" alt="{esc(a["afbeelding_alt"])}" loading="lazy">'
    else:
        beeld = f'<div class="news-card-placeholder" aria-hidden="true">{esc(a["titel"][:1])}</div>'
    pijl = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/>'
            '<polyline points="12 5 19 12 12 19"/></svg>')
    imgcls = "news-card-img news-card-img--logo" if a["afbeelding_stijl"] == "logo" else "news-card-img"
    return f"""      <article class="news-card aos d{vertraging}">
        <a href="{esc(href)}"{target} class="{imgcls}" aria-hidden="true" tabindex="-1">{beeld}</a>
        <div class="news-card-body">
          <div class="news-card-cat">{esc(a['categorie'])} &middot; <time datetime="{a['datum'].isoformat()}">{datum_nl(a['datum'])}</time></div>
          <h3><a href="{esc(href)}"{target}>{esc(a['titel'])}</a></h3>
          <p>{esc(a['samenvatting'])}</p>
          <a href="{esc(href)}"{target} class="news-card-cta">{cta} {pijl}</a>
        </div>
      </article>
"""


def cta_sectie() -> str:
    return """<!-- ═══ CTA ═══ -->
<section class="cta-section section" aria-labelledby="cta-blog">
  <div class="cta-inner">
    <span class="eyebrow eyebrow-light">Vragen?</span>
    <h2 id="cta-blog">Herkent u dit in uw eigen praktijk?</h2>
    <p>Neem gerust contact op. Wij denken graag met u mee over uw administratie en declaraties.</p>
    <div class="cta-actions">
      <a href="/contact" class="btn btn-primary btn-lg">Contact opnemen</a>
      <a href="/quickscan" class="btn btn-white-outline btn-lg">Doe de quickscan</a>
    </div>
  </div>
</section>

</main>

"""


def bouw_overzicht(schil, artikelen) -> str:
    url = f"{BASE_URL}/blog"
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "Blog", "name": "Blog", "url": url,
        "publisher": {"@type": "Organization", "name": SITE_NAAM, "url": BASE_URL + "/"},
        "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": url}]},
    }, ensure_ascii=False, indent=2)
    kaarten = "".join(kaart(a, (i % 2) + 1) for i, a in enumerate(artikelen))
    if not kaarten:
        kaarten = '      <p class="lead">De eerste artikelen verschijnen binnenkort.</p>\n'
    return head(schil, titel="Blog", url=url, og_image=STANDAARD_OG,
                beschrijving="Artikelen over GGZ- en jeugdzorgadministratie, declareren, "
                             "software en het ondernemen als zorgpraktijk, door CONTI-NU Bedrijfsondersteuning.",
                extra=f'  <script type="application/ld+json">\n{ld}\n  </script>') + schil["nav"] + f"""
<!-- ═══ PAGE HERO ═══ -->
<header class="page-hero">
  <div class="page-hero-inner">
    <span class="eyebrow">Blog</span>
    <h1>Kennis &amp; nieuws voor zorgpraktijken</h1>
    <p class="lead">Artikelen over administratie, declareren, software en ondernemen in de GGZ en jeugdzorg. Geschreven vanuit de praktijk van CONTI-NU.</p>
    <nav class="breadcrumb" aria-label="Kruimelpad">
      <a href="/">Home</a>
      <span class="breadcrumb-sep" aria-hidden="true">/</span>
      <strong class="breadcrumb-current" aria-current="page">Blog</strong>
    </nav>
  </div>
</header>

<main>

<!-- ═══ ARTIKELEN ═══ -->
<section class="section" aria-labelledby="blog-heading">
  <div class="container">
    <h2 id="blog-heading" class="visually-hidden">Artikelen</h2>
    <div class="news-grid">
{kaarten}    </div>

    <div class="blog-volg aos">
      <p>Nieuwe artikelen delen we ook op
        <a href="https://www.linkedin.com/company/conti-nu/" target="_blank" rel="noopener noreferrer">LinkedIn</a>.
        Volg ons daar om als eerste op de hoogte te zijn.</p>
    </div>
  </div>
</section>

""" + cta_sectie() + schil["staart"] + "</body>\n</html>\n"


def bouw_artikel(schil, a, overige) -> str:
    url = a["url"]
    og_image = a["afbeelding_url"] or STANDAARD_OG
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": a["titel"], "description": a["samenvatting"], "url": url,
        "datePublished": a["datum"].isoformat(), "dateModified": a["datum"].isoformat(),
        "image": og_image, "inLanguage": "nl-NL",
        "author": {"@type": "Person", "name": a["auteur"]},
        "publisher": {"@type": "Organization", "name": SITE_NAAM, "url": BASE_URL + "/",
                      "logo": {"@type": "ImageObject", "url": BASE_URL + "/Assets/favicon.png"}},
        "mainEntityOfPage": url,
    }, ensure_ascii=False, indent=2)
    body = markdown.markdown(a["body_md"], extensions=["extra", "sane_lists", "toc"], output_format="html5")
    figuur = ""
    if a["afbeelding_pad"]:
        figuur = f"""
    <figure class="post-figure aos">
      <img src="{esc(a['afbeelding_pad'])}" alt="{esc(a['afbeelding_alt'])}" width="1200" height="675">
    </figure>"""
    deel_url = html.escape(url, quote=True)
    meer = "".join(kaart(b, (i % 2) + 1) for i, b in enumerate(overige[:2]))
    meer_blok = f"""
<section class="section section-cream" aria-labelledby="meer-heading">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Verder lezen</span>
      <h2 id="meer-heading">Meer artikelen</h2>
    </div>
    <div class="news-grid">
{meer}    </div>
  </div>
</section>
""" if meer else ""
    return head(schil, titel=a["titel"], beschrijving=a["samenvatting"], url=url, og_image=og_image,
                og_type="article", trefwoorden=a["trefwoorden"],
                extra=(f'  <meta property="article:published_time" content="{a["datum"].isoformat()}">\n'
                       f'  <meta property="article:author" content="{esc(a["auteur"])}">\n'
                       f'  <script type="application/ld+json">\n{ld}\n  </script>')) + schil["nav"] + f"""
<!-- ═══ PAGE HERO ═══ -->
<header class="page-hero">
  <div class="page-hero-inner">
    <span class="eyebrow">{esc(a['categorie'])}</span>
    <h1>{esc(a['titel'])}</h1>
    <p class="lead">{esc(a['samenvatting'])}</p>
    <p class="post-meta">
      <time datetime="{a['datum'].isoformat()}">{datum_nl(a['datum'])}</time>
      <span aria-hidden="true">&middot;</span> {a['leestijd']} min leestijd
      <span aria-hidden="true">&middot;</span> {esc(a['auteur'])}
    </p>
    <nav class="breadcrumb" aria-label="Kruimelpad">
      <a href="/">Home</a>
      <span class="breadcrumb-sep" aria-hidden="true">/</span>
      <a href="/blog">Blog</a>
      <span class="breadcrumb-sep" aria-hidden="true">/</span>
      <strong class="breadcrumb-current" aria-current="page">{esc(a['titel'])}</strong>
    </nav>
  </div>
</header>

<main>

<!-- ═══ ARTIKEL ═══ -->
<article class="section post" aria-labelledby="post-title">
  <div class="container post-container">{figuur}
    <div class="post-body">
{body}
    </div>
    <div class="post-share">
      <span>Deel dit artikel</span>
      <a class="btn btn-outline" href="https://www.linkedin.com/sharing/share-offsite/?url={deel_url}" target="_blank" rel="noopener noreferrer">
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6zM2 9h4v12H2z"/><circle cx="4" cy="4" r="2"/></svg>
        Delen op LinkedIn
      </a>
      <a class="btn btn-outline" href="mailto:?subject={esc(a['titel'])}&amp;body={deel_url}">E-mail</a>
      <a class="post-terug" href="/blog">&larr; Alle artikelen</a>
    </div>
  </div>
</article>
{meer_blok}
""" + cta_sectie() + schil["staart"] + "</body>\n</html>\n"


# ── Sitemap, feed, JSON ──────────────────────────────────────────────────
def werk_sitemap_bij(artikelen):
    pad = ROOT / "sitemap.xml"
    xml = pad.read_text(encoding="utf-8")
    xml = re.sub(r"\s*<url>\s*<loc>[^<]*/(blog|nieuws)[^<]*</loc>.*?</url>", "", xml, flags=re.S)
    vandaag = date.today().isoformat()
    blok = [f"""
  <url>
    <loc>{BASE_URL}/blog</loc>
    <lastmod>{vandaag}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
"""]
    for a in artikelen:
        if a["link"]:
            continue
        blok.append(f"""
  <url>
    <loc>{a['url']}</loc>
    <lastmod>{a['datum'].isoformat()}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
""")
    xml = xml.replace("</urlset>", "".join(blok) + "\n</urlset>")
    pad.write_text(xml, encoding="utf-8")


def schrijf_feed(artikelen):
    items = []
    for a in artikelen:
        beeld = f"\n      <enclosure url=\"{a['afbeelding_url']}\" type=\"image/jpeg\" length=\"0\"/>" if a["afbeelding_url"] else ""
        pub = datetime.combine(a["datum"], datetime.min.time()).strftime("%a, %d %b %Y 08:00:00 +0100")
        items.append(f"""    <item>
      <title>{esc(a['titel'])}</title>
      <link>{a['url']}</link>
      <guid isPermaLink="true">{a['url']}</guid>
      <pubDate>{pub}</pubDate>
      <category>{esc(a['categorie'])}</category>
      <description>{esc(a['samenvatting'])}</description>{beeld}
    </item>""")
    (UIT / "feed.xml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{SITE_NAAM} — Blog</title>
    <link>{BASE_URL}/blog</link>
    <atom:link href="{BASE_URL}/blog/feed.xml" rel="self" type="application/rss+xml"/>
    <description>Artikelen over GGZ- en jeugdzorgadministratie, declareren en software.</description>
    <language>nl-nl</language>
{chr(10).join(items)}
  </channel>
</rss>
""", encoding="utf-8")


def schrijf_json(artikelen):
    data = {"generated_at": datetime.now().isoformat(timespec="seconds"), "site": "conti_nu", "articles": []}
    for a in artikelen:
        data["articles"].append({
            "slug": a["slug"], "title": a["titel"], "url": a["url"], "external": bool(a["link"]),
            "date": a["datum"].isoformat(), "category": a["categorie"], "summary": a["samenvatting"],
            "image_url": a["afbeelding_url"], "author": a["auteur"], "keywords": a["trefwoorden"],
            "linkedin_text": a["linkedin"], "status": a["status"],
        })
    (UIT / "artikelen.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ── Main ─────────────────────────────────────────────────────────────────
def main():
    met_concept = "--concept" in sys.argv
    schil = laad_schil()
    alle = [lees_artikel(p) for p in sorted(BRON.glob("*.md")) if not p.name.startswith(("LEESMIJ", "_"))]
    zichtbaar = [a for a in alle if a["status"] == "gepubliceerd" or met_concept]
    zichtbaar.sort(key=lambda a: a["datum"], reverse=True)
    UIT.mkdir(exist_ok=True)

    # Oude uitvoer opruimen (artikelen die weg of concept zijn), bron en index ongemoeid
    verwacht = {f"{a['slug']}.html" for a in zichtbaar if not a["link"]} | {"index.html"}
    for oud in UIT.glob("*.html"):
        if oud.name not in verwacht:
            oud.unlink()

    for a in zichtbaar:
        if a["link"]:
            continue
        overige = [b for b in zichtbaar if b is not a and not b["link"]]
        (UIT / f"{a['slug']}.html").write_text(bouw_artikel(schil, a, overige), encoding="utf-8")
    (UIT / "index.html").write_text(bouw_overzicht(schil, zichtbaar), encoding="utf-8")
    schrijf_feed(zichtbaar)
    schrijf_json(zichtbaar)
    werk_sitemap_bij(zichtbaar)

    eigen = sum(1 for a in zichtbaar if not a["link"])
    concept = sum(1 for a in alle if a["status"] != "gepubliceerd")
    print(f"Blog gebouwd: {eigen} artikel(en), {len(zichtbaar) - eigen} extern, {concept} concept"
          + (" (meegenomen)" if met_concept and concept else "") + ".")
    for a in zichtbaar:
        print(f"  {a['datum']}  {a['titel']}  →  {a['url']}")


if __name__ == "__main__":
    main()
