# HANDOFF — 3 nieuwe blogartikelen + oranje tussenkopjes (11 sep 2026)

## ✅ Addendum (11 sep 2026, later) — gemerged, gepusht, live geverifieerd

Status is niet meer "klaar voor merge" maar **AFGEROND**:

- `main` bevat de merge (`303bd10`), gepusht naar `origin/main` — door Elio
  gedaan (ik kan hier niet naar `main` pushen, deploy-guard).
- **Uitrol (rsync) is ook al gebeurd** — geverifieerd met een live check,
  niet aangenomen:
  - `https://www.conti-nu.nl/blog/visitatie-lvvp-kwaliteitscriteria` → 200
  - `https://www.conti-nu.nl/blog/jaareinde-checklist-ggz-jeugdzorg` → 200
  - `https://www.conti-nu.nl/blog/kwetsbare-zorgadministratie-quickscan` → 200
  - alle 3 staan in `/blog/`-overzicht
  - live CSS bevestigd: `.post-body h3 { ... color: var(--orange); }` staat
    in de uitgerolde `css/style.css`
- **Extra vraag van Elio deze sessie**: of er onder elk artikel een link naar
  het contactformulier + een Quickscan-knop kan. Antwoord: bestond al,
  ongewijzigd — `cta_sectie()` in `build_blog.py` (regel 180-196) hangt
  automatisch onder ELK artikel (ook de 3 nieuwe, bevestigd in de
  gegenereerde HTML): "Contact opnemen" → `/contact`, "Doe de quickscan" →
  `/quickscan`. Geen code-wijziging nodig, Elio bevestigd akkoord.
- **Openstaand punt blijft openstaand** (zie hieronder): de
  bullet-round-trip-bug in de rich-text-editor van de Blog-module in
  `integration_dashboard` — niet in deze branch aangepakt.

Geen verdere actie nodig op dit onderwerp.

---

Aanleiding: Dunja meldde bij Elio dat ze haar visitatie-artikel niet live kon
zetten ("Page not found") en dat ze na teruggaan naar "haar blog" totaal
andere tekst zag, mist de tussenkopjes die ze had toegevoegd. Elio gaf
daarna ook 3 Word-documenten (`~/Downloads/conti-nu/blogs/`) door om als
nieuwe blogartikelen te publiceren.

## Branch / basis / commits / status

- Repo: `meklouwen/conti-nu-website` (los van `integration_dashboard`, apart
  `.git`, lokaal uitgecheckt op `/Users/Elio/Documents/Zakelijk/PayIBAN/conti-nu-website`).
- Branch: `feat/drie-nieuwe-blogartikelen-oranje-kopjes`, basis `origin/main`
  (tip `14865fc`), **1 commit**: `bf21894`.
- Status: **lokaal af + lokaal gebouwd en gecontroleerd, gepusht**
  (`origin/feat/drie-nieuwe-blogartikelen-oranje-kopjes` staat op dezelfde
  tip). **Niet gemerged naar `main`, niet uitgerold (nog niet live).**
- Deze repo kent geen deploy-chat/CI zoals `integration_dashboard` — uitrol
  is altijd handmatig (build + rsync vanaf Elio's Mac, zie LEESMIJ.md).

## Wat er gebeurde (root cause, bevestigd via git-geschiedenis)

Dunja schreef haar visitatie-artikel in `blog/_bron/voorbeeld-artikel.md`
— het meegeleverde VOORBEELDbestand — in plaats van een nieuw bestand aan
te maken (de samenvatting van dat bestand zegt letterlijk "kopieer het
bestand als startpunt voor een echt artikel", maar dat is makkelijk te
missen). 3 opeenvolgende saves vandaag (13:40–13:55), laatste actie: status
`concept` → `gepubliceerd`. Niets is verloren gegaan; alles stond veilig in
git (commits `106be1d` → `2eb7ccf` → `14865fc`, lineaire keten, geen
conflict).

- **"Page not found"**: het dashboard commit alleen de tekst naar GitHub.
  De site is een statische build (`build_blog.py`) die daarna nog
  handmatig gebouwd + uitgerold moet worden. Die build was voor het laatst
  gedraaid op 9 sep 20:06 — dus vóór haar artikel bestond, vandaar de 404.
- **"Terug naar mijn blog, tekst totaal anders, kopjes weg"**: hetzelfde —
  de laatst gebouwde `blog/index.html`/`artikelen.json` bevatten alleen de
  2 oude externe artikelen (HCI, ZZP Nederland), niet haar nieuwe tekst.

## Wat & waarom (deze branch)

1. **`voorbeeld-artikel.md` teruggezet** naar de originele, schone
   template-inhoud (`status: concept`) — zodat dit sjabloon weer veilig als
   voorbeeld dient en niet per ongeluk een derde keer als echt artikel
   wordt gebruikt.
2. **3 nieuwe artikelen** aangemaakt met eigen bestandsnaam/slug, uit de
   aangeleverde content (Dunja's git-geschiedenis voor het visitatie-stuk,
   de 2 Word-documenten voor de andere twee):
   - `blog/_bron/visitatie-lvvp-kwaliteitscriteria.md` — "Wat houdt een
     visitatie in de ggz eigenlijk in?"
   - `blog/_bron/jaareinde-checklist-ggz-jeugdzorg.md` — "Het jaar
     afsluiten — dit moet u als ggz- of jeugdzorgpraktijk nog regelen"
   - `blog/_bron/kwetsbare-zorgadministratie-quickscan.md` — "Hoe
     kwetsbaar is de zorgadministratie van uw praktijk eigenlijk?"
   Alle 3: `status: gepubliceerd`, `datum: 2026-09-11`, eigen categorie/
   trefwoorden/samenvatting/linkedin-tekst, geen afbeelding (geen foto's
   aangeleverd — optioneel veld, mag later toegevoegd worden).
3. **CSS**: `.post-body h3 { color: var(--orange) }` toegevoegd
   (`css/style.css`) — dit is waar Dunja's "oranje kopjes" op sloegen.
   Voorheen hadden `h2` én `h3` in een artikel dezelfde (donkerbruine)
   kleur; nu krijgen de sub-tussenkopjes (`### `) het merk-oranje
   (`var(--orange)`, dezelfde kleur die de site al overal gebruikt).
4. **`python3 build_blog.py` gedraaid** — de gegenereerde bestanden
   (`blog/*.html`, `blog/artikelen.json`, `blog/index.html`,
   `blog/feed.xml`, `sitemap.xml`) zitten al in deze commit, dus een
   hernieuwde build is bij het uitrollen niet per se nodig (maar wel
   verstandig als er tussentijds iets anders is gewijzigd op `main`).

## Gewijzigde bestanden

| Bestand | Wat | Merge-risico |
|---|---|---|
| `blog/_bron/voorbeeld-artikel.md` | teruggezet naar schone template | geen |
| `blog/_bron/visitatie-lvvp-kwaliteitscriteria.md` (nieuw) | artikel 1 | geen |
| `blog/_bron/jaareinde-checklist-ggz-jeugdzorg.md` (nieuw) | artikel 2 | geen |
| `blog/_bron/kwetsbare-zorgadministratie-quickscan.md` (nieuw) | artikel 3 | geen |
| `css/style.css` | 1 regel, h3-kleur | geen |
| `blog/*.html`, `blog/index.html`, `blog/artikelen.json`, `blog/feed.xml`, `sitemap.xml` | **gegenereerd** door `build_blog.py` — niet handmatig bewerken | **let op**: als er ondertussen (bv. door de dashboard-editor) al een nieuwere build op `main` staat, dan wint de laatste build — vóór mergen even checken of `main` intussen niet al verder is dan `14865fc`, en zo ja: opnieuw `python3 build_blog.py` draaien na de merge |

## Config / data / env

- Geen env-vars, geen aparte config. Wel: de dashboard-blogeditor
  (`integration_dashboard` → `/klant/conti-nu/blog`) schrijft rechtstreeks
  naar `blog/_bron/*.md` in déze repo via de GitHub Contents API — als
  Dunja tussen nu en de merge nog iets bewerkt via het dashboard, kan dat
  op `main` een nieuwere commit zetten die deze branch niet heeft. Kort
  vóór mergen `git log origin/main` checken.

## Verificatie

- `python3 build_blog.py` lokaal gedraaid: "Blog gebouwd: 3 artikel(en), 2
  extern, 1 concept" — geen fouten.
- Gegenereerde HTML gecontroleerd (`grep` op `<h2>`/`<h3>`/`<ul><li>`):
  koppen en opsommingen renderen correct als echte markdown-structuur.
- **Niet getest:** de daadwerkelijke pagina in een browser (geen lokale
  webserver gestart), en de oranje h3-kleur is alleen in de CSS-bron
  gecontroleerd, niet visueel in een browser bekeken. Aanbevolen: na
  uitrol 1 artikel openen en de tussenkopjes met het blote oog checken.

## Open punten

- **Bekende, apart te onderzoeken bug** (niet in deze branch gefixt): de
  markdown die Dunja via de dashboard-editor opsloeg bevatte letterlijke
  "•      "-bullet-tekens in plaats van echte markdown `- `-opsommingen
  (zichtbaar in de commits van vandaag vóór deze branch). Vermoedelijk een
  round-trip-bug in de rich-text-editor van de Blog-module
  (`app/templates/partials/_rich_editor.html` in `integration_dashboard`)
  die bulletlijsten niet correct naar markdown terugzet. Niet blokkerend
  voor deze publicatie (ik heb de 3 nieuwe artikelen met de hand met
  correcte `- `-syntax geschreven), maar zal opnieuw misgaan zodra iemand
  via de editor zelf een opsomming maakt. Los te onderzoeken in
  `integration_dashboard`.
- Geen beslissing van Elio nodig om te mergen — dit is contentwerk, geen
  architectuurkeuze.

## Deploy

- **Geen deploy-chat voor deze repo** — dit is Elio's eigen handmatige
  traject (zie `blog/_bron/LEESMIJ.md`):
  1. `git checkout main && git pull --ff-only origin main`
  2. `git merge --no-ff feat/drie-nieuwe-blogartikelen-oranje-kopjes`
  3. Zo nodig opnieuw `python3 build_blog.py` (zie waarschuwing hierboven
     bij "gegenereerde bestanden")
  4. `git push origin main`
  5. Uitrollen zoals de rest van de site: **rsync naar de VPS** — dit is
     de stap die ik niet kan doen; ik heb geen rsync-doel/credentials voor
     conti-nu.nl. Elio: dit is dezelfde stap die je al voor eerdere
     site-wijzigingen hebt gedaan.
- **Na uitrol verifiëren**: `https://www.conti-nu.nl/blog/` open, de 3
  nieuwe artikelen moeten in het overzicht staan; open 1 artikel en
  controleer dat de tussenkopjes (`### `) oranje zijn.
- Opruimen: geen worktree gebruikt voor deze branch (rechtstreeks in de
  bestaande lokale checkout gewerkt); branch kan na de merge lokaal en op
  GitHub verwijderd worden (`git branch -d feat/drie-nieuwe-blogartikelen-oranje-kopjes`,
  `git push origin --delete feat/drie-nieuwe-blogartikelen-oranje-kopjes`).
