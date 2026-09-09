#!/usr/bin/env python3
"""
Reviews-generator voor conti-nu.nl — fase 1 (Elio, 9 sep 2026): eenvoudig
bestaande reviews tonen op één pagina. Fase 2 (eenvoudig een review
toevoegen) en fase 3 (uitnodigingsmail + publieke invulpagina) volgen later
in het dashboard; dit script is bewust hetzelfde eenvoudige "markdown-bron
→ statische pagina"-recept als build_blog.py, zodat "een review toevoegen"
vanaf dag 1 al simpel is: nieuw bestand in reviews/_bron/, script draaien.

Bron:   reviews/_bron/<slug>.md   (kopblok: naam, functie, datum, evt. afbeelding)
Uit:    reviews.html               (alle gepubliceerde reviews, nieuwste eerst)
        sitemap.xml                (reviews-URL toegevoegd/bijgewerkt)

Gebruik:  python3 build_reviews.py            # alleen 'status: gepubliceerd'
          python3 build_reviews.py --concept  # neemt ook concepten mee (lokaal nakijken)

Hergebruikt de site-schil (nav/footer/tracking) en de head()/cta_sectie()-
bouwstenen van build_blog.py — geen tweede implementatie van diezelfde HTML.
De opmaak van elke review is de bestaande .testimonial-stijl uit index.html
(zie css/style.css), dus dit ziet er hetzelfde uit als de twee reviews die al
op de homepage staan.
"""
import html
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from build_blog import BASE_URL, SITE_NAAM, STANDAARD_OG, cta_sectie, esc, head, laad_schil  # noqa: E402

BRON = ROOT / "reviews" / "_bron"
UIT = ROOT / "reviews.html"


def lees_review(pad: Path) -> dict:
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
    for verplicht in ("naam", "functie", "datum"):
        if not meta.get(verplicht):
            sys.exit(f"{pad.name}: '{verplicht}' ontbreekt in het kopblok")
    try:
        d = date.fromisoformat(meta["datum"])
    except ValueError:
        sys.exit(f"{pad.name}: datum moet als 2026-09-09 geschreven zijn")

    afbeelding = meta.get("afbeelding", "")
    if afbeelding and not afbeelding.startswith(("http://", "https://", "/")):
        afbeelding = "/" + afbeelding
    return {
        "slug": pad.stem,
        "naam": meta["naam"],
        "functie": meta["functie"],
        "datum": d,
        "afbeelding": afbeelding,
        "status": meta.get("status", "gepubliceerd").lower(),
        "tekst": body.strip(),
    }


def kaart(r: dict, vertraging: int) -> str:
    avatar = ""
    if r["afbeelding"]:
        avatar = (f'<div class="testimonial-avatar" aria-hidden="true">'
                  f'<img src="{esc(r["afbeelding"])}" alt="{esc(r["naam"])}"></div>')
    return f"""      <blockquote class="testimonial aos d{vertraging}">
        <div class="testimonial-open-quote" aria-hidden="true">&ldquo;</div>
        <p class="testimonial-text">
          {esc(r['tekst'])}
        </p>
        <footer class="testimonial-author">
          {avatar}
          <div>
            <div class="testimonial-name">{esc(r['naam'])}</div>
            <div class="testimonial-role">{esc(r['functie'])}</div>
          </div>
        </footer>
      </blockquote>
"""


def bouw_pagina(schil, reviews) -> str:
    url = f"{BASE_URL}/reviews"
    ld = html_ld(reviews, url)
    kaarten = "".join(kaart(r, (i % 2) + 1) for i, r in enumerate(reviews))
    if not kaarten:
        kaarten = '      <p class="lead">De eerste reviews verschijnen binnenkort.</p>\n'
    return head(schil, titel="Reviews", url=url, og_image=STANDAARD_OG,
                beschrijving="Ervaringen van klanten van CONTI-NU Bedrijfsondersteuning — "
                             "GGZ- en jeugdzorgpraktijken over administratie, declareren en samenwerking.",
                extra=f'  <script type="application/ld+json">\n{ld}\n  </script>') + schil["nav"] + f"""
<!-- ═══ PAGE HERO ═══ -->
<header class="page-hero">
  <div class="page-hero-inner">
    <span class="eyebrow">Reviews</span>
    <h1>Wat klanten van CONTI-NU zeggen</h1>
    <p class="lead">Echte ervaringen van GGZ- en jeugdzorgpraktijken die met ons samenwerken.</p>
    <nav class="breadcrumb" aria-label="Kruimelpad">
      <a href="/">Home</a>
      <span class="breadcrumb-sep" aria-hidden="true">/</span>
      <strong class="breadcrumb-current" aria-current="page">Reviews</strong>
    </nav>
  </div>
</header>

<main>

<!-- ═══ REVIEWS ═══ -->
<section class="section" aria-labelledby="reviews-heading">
  <div class="container">
    <h2 id="reviews-heading" class="visually-hidden">Reviews</h2>
    <div class="testimonials-grid">
{kaarten}    </div>
  </div>
</section>

""" + cta_sectie() + schil["staart"] + "</body>\n</html>\n"


def html_ld(reviews, url) -> str:
    import json
    items = [{
        "@type": "Review",
        "author": {"@type": "Person", "name": r["naam"]},
        "datePublished": r["datum"].isoformat(),
        "reviewBody": r["tekst"],
        "itemReviewed": {"@type": "Organization", "name": SITE_NAAM},
    } for r in reviews]
    ld = {
        "@context": "https://schema.org", "@type": "CollectionPage", "name": "Reviews", "url": url,
        "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "Reviews", "item": url}]},
        "mainEntity": items,
    }
    return json.dumps(ld, ensure_ascii=False, indent=2)


def werk_sitemap_bij():
    pad = ROOT / "sitemap.xml"
    xml = pad.read_text(encoding="utf-8")
    xml = re.sub(r"\s*<url>\s*<loc>[^<]*/reviews</loc>.*?</url>", "", xml, flags=re.S)
    vandaag = date.today().isoformat()
    blok = f"""
  <url>
    <loc>{BASE_URL}/reviews</loc>
    <lastmod>{vandaag}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
"""
    xml = xml.replace("</urlset>", blok + "\n</urlset>")
    pad.write_text(xml, encoding="utf-8")


def main():
    met_concept = "--concept" in sys.argv
    schil = laad_schil()
    # laad_schil() zet 'active' op de /blog-link (blog-specifiek) — voor deze
    # pagina hoort 'active' op /reviews te staan, niet op /blog. Whitespace-
    # tolerant (build_blog.py's eigen sub gebruikt ook \s*, dus de precieze
    # spatiëring hangt af van over.html's bronopmaak).
    nav = re.sub(r'(href="/blog"\s*class="nav-link)\s+active"', r'\1"', schil["nav"])
    nav = re.sub(r'(href="/reviews"\s*class="nav-link)"', r'\1 active"', nav)
    schil["nav"] = nav

    alle = [lees_review(p) for p in sorted(BRON.glob("*.md"), reverse=True) if not p.name.startswith(("LEESMIJ", "_"))]
    zichtbaar = [r for r in alle if r["status"] == "gepubliceerd" or met_concept]
    zichtbaar.sort(key=lambda r: r["datum"], reverse=True)

    UIT.write_text(bouw_pagina(schil, zichtbaar), encoding="utf-8")
    werk_sitemap_bij()

    concept = sum(1 for r in alle if r["status"] != "gepubliceerd")
    print(f"Reviews gebouwd: {len(zichtbaar)} review(s)"
          + (f", {concept} concept" + (" (meegenomen)" if met_concept else " (overgeslagen)") if concept else "")
          + ".")
    for r in zichtbaar:
        print(f"  {r['datum']}  {r['naam']}  —  {r['functie']}")


if __name__ == "__main__":
    main()
