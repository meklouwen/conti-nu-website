# Blog schrijven voor conti-nu.nl

Elk artikel is één Markdown-bestand in deze map. De bestandsnaam wordt de URL:
`declareren-in-de-ggz.md` → `https://www.conti-nu.nl/blog/declareren-in-de-ggz`.
Gebruik kleine letters en koppeltekens, geen spaties.

## Kopblok (bovenaan het bestand)

```
---
titel: Wat verandert er in 2027 voor GGZ-declaraties?
datum: 2026-09-15
categorie: Declareren
samenvatting: In twee zinnen waar het artikel over gaat. Dit is ook de tekst die op LinkedIn en in Google verschijnt.
afbeelding: declareren-2027.jpg
afbeelding_alt: Behandelaar achter laptop met declaratieoverzicht
auteur: Dunja Tagliola-Spaan
status: gepubliceerd
trefwoorden: ggz declaraties 2027, zorgprestatiemodel, declareren ggz
linkedin: Korte, persoonlijke tekst als voorstel voor de LinkedIn-post. Mag leeg blijven.
---
```

- **titel, datum, samenvatting** zijn verplicht. Datum als `2026-09-15`.
- **afbeelding**: zet de foto in `Assets/blog/` (liggend, minimaal 1200×675 px, jpg).
  Eén foto doet drie dingen: kaart in het overzicht, kop van het artikel, én de
  voorvertoning als het artikel op LinkedIn wordt gedeeld.
- **afbeelding_stijl**: `logo` als het beeld een logo is (past in de kaart i.p.v. vullen).
- **status**: `concept` = wel bewaren, nog niet online. `gepubliceerd` = online bij de eerstvolgende build.
- **link** (optioneel): voor een verwijzing naar een artikel elders. Dan komt er alleen een kaart in het
  overzicht die daarheen linkt, geen eigen pagina. Geef dan ook `bron: Naam van de site` op.

## Tekst

Onder het kopblok gewoon Markdown: `## Tussenkop`, alinea's, `- opsomming`, **vet**, `> citaat`.
Foto's in de tekst: `![omschrijving](/Assets/blog/foto.jpg)`.

Richtlijnen die goed werken voor deze site:
- 600–1000 woorden, één onderwerp, tussenkoppen om de 150 woorden.
- Schrijf vanuit de praktijk: wat ziet Conti-nu bij klanten, wat is het advies.
- Eindig met wat de lezer nu kan doen (de pagina krijgt automatisch een contact/quickscan-blok).

## Online zetten

```
python3 build_blog.py          # bouwt blog/, sitemap en feed
python3 build_blog.py --concept  # ook concepten, om lokaal na te kijken
```

Daarna committen en uitrollen zoals de rest van de site (rsync naar de VPS).
De blog verschijnt in het menu onder **Blog**; `/nieuws` stuurt door naar `/blog`.
