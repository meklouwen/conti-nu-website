# Reviews toevoegen

Zet hier een `.md`-bestand per review (bestandsnaam = slug, mag alles zijn,
verschijnt nergens in een URL — reviews hebben geen eigen pagina, ze staan
allemaal samen op `/reviews`).

Kopblok (verplicht: naam, functie, datum; rest optioneel):

```
---
naam: Voornaam Achternaam
functie: Functietitel, Bedrijfsnaam
datum: 2026-09-09
afbeelding: Assets/foto-van-de-persoon.jpg
status: gepubliceerd
---
De review-tekst zelf, gewoon platte tekst of een paar Markdown-regels.
```

- `afbeelding` is optioneel — zonder foto toont de review gewoon zonder
  avatar, dat is prima.
- `status: concept` houdt een review buiten `/reviews` totdat je 'm klaar
  vindt. Bouw met `python3 build_reviews.py --concept` om concepten toch
  even lokaal te bekijken.
- Nieuwste datum verschijnt boven aan de pagina.

Bouwen: `python3 build_reviews.py` (vanuit de root van deze repo).
