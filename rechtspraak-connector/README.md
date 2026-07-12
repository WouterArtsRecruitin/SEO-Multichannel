# Rechtspraak API Connector — Gelre Advocaten

Haalt automatisch nieuwe **jurisprudentie** op uit de openbare **Rechtspraak
Open Data API**, filtert die op de vakgebieden van Gelre Advocaten, en exporteert
het schoon en gestructureerd naar **Supabase (PostgreSQL)** en/of **Obsidian
(Markdown)** — voorbereid zodat er later een **RAG/MCP-chatagent** op gebouwd kan
worden.

> Fair-use: de connector is bewust getemperd (max requests/minuut + minimale
> tussentijd) en draait één keer per nacht. Zo overbelast je de Rechtspraak-
> servers niet.

## Hoe het werkt (architectuur)

```
                 ┌────────────────────────────────────────────────────────┐
   nachtelijke   │                     Pipeline (agent)                    │
   cron/timer ─▶ │  1. discover   2. fetch      3. filter   4. export      │
                 │     zoeken        content        keywords    md/supabase │
                 │     (Atom)        (XML)                      5. reconcile │
                 └───────┬───────────────┬───────────────────────┬─────────┘
                         │               │                       │
              data.rechtspraak.nl        │                 ┌─────┴──────┐
              /uitspraken/zoeken   /uitspraken/content   Supabase     Obsidian
              (gefilterde ECLI's)  (volledige uitspraak) (PostgreSQL) (Markdown)
```

1. **Discover** — `GET /uitspraken/zoeken` levert een **Atom-feed** met de ECLI's
   die matchen op je filters (`subject`=rechtsgebied, `type`, `creator`,
   `modified`-range voor incrementeel). Gepagineerd via `from`/`max`.
2. **Fetch** — per ECLI `GET /uitspraken/content?id=ECLI...` → volledige XML
   (RDF-metadata + `<uitspraak>`/`<conclusie>`-body).
3. **Filter** — client-side keyword-filter (any/all/off) op titel+samenvatting+tekst.
4. **Export** — idempotente upsert naar Supabase en/of één Markdown-bestand per ECLI.
5. **Reconcile** — hercontroleert eerder opgeslagen ECLI's; ingetrokken/verwijderde
   zaken worden op `withdrawn` gezet **plus** logging/notificatie.

De run is **incrementeel**: de laatste `modified`-tijd wordt bewaard (`.state.json`
of `run_log`), zodat elke nacht alleen nieuw/gewijzigd werk wordt opgehaald.

## Directorystructuur

```
rechtspraak-connector/
├── README.md
├── requirements.txt              # requests + PyYAML (XML = stdlib); psycopg optioneel
├── .env.example                  # DATABASE_URL, NOTIFY_WEBHOOK_URL
├── config/
│   └── config.example.yaml       # rechtsgebieden, keywords, rate-limit, export-target
├── db/
│   └── schema.sql                # Supabase/PostgreSQL schema (+ optioneel pgvector)
├── scripts/
│   ├── run_daily.py              # entrypoint voor cron (laadt .env)
│   └── crontab.example           # cron- én systemd-timer-voorbeeld
└── src/rechtspraak_connector/
    ├── config.py                 # YAML + env laden/valideren
    ├── client.py                 # RechtspraakClient + RateLimiter (de core loop)
    ├── parser.py                 # Atom- en content-XML parsen (stdlib)
    ├── models.py                 # EcliSummary, Uitspraak (metadata ≠ hoofdtekst)
    ├── pipeline.py               # de nachtelijke agent (discover→export→reconcile)
    ├── reconcile → in pipeline._reconcile()
    ├── notify.py                 # log + optionele Slack/Teams-webhook
    ├── cli.py                    # `run` en `test`
    └── exporters/
        ├── markdown_exporter.py  # Obsidian: YAML-frontmatter + schone body
        └── supabase_exporter.py  # PostgreSQL upsert (psycopg 3)
```

## Databaseschema (Supabase)

Kern: **metadata staat los van de hoofdtekst** (`inhoud`), zodat je later kunt
chunken/embedden voor RAG zonder de metadata te vervuilen.

| tabel | belangrijkste kolommen |
|-------|------------------------|
| `uitspraken` | `ecli` (PK), `type`, `titel`, `samenvatting`, `instantie`, `rechtsgebieden text[]`, `uitspraakdatum`, `publicatiedatum`, `modified`, `vindplaatsen jsonb`, **`inhoud` (schone tekst)**, **`metadata jsonb` (ruwe metadata)**, `content_hash`, `status` (`active`/`withdrawn`), `first_seen`, `last_checked` |
| `run_log` | per run: `found`, `inserted`, `updated`, `withdrawn`, `errors`, `ok`, `notes` |
| `uitspraak_chunks` *(optioneel, pgvector)* | `ecli` (FK), `chunk_index`, `inhoud`, `embedding vector` |

Volledige DDL: **`db/schema.sql`** (draai in de Supabase SQL-editor of met `psql`).

## Installeren & draaien

```bash
cd rechtspraak-connector
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # + 'psycopg[binary]' als je Supabase gebruikt

cp .env.example .env                      # vul DATABASE_URL (alleen bij Supabase)
cp config/config.example.yaml config/config.yaml   # zet je rechtsgebieden/keywords

# 1) droogtest — eerste pagina resultaten, geen export:
PYTHONPATH=src python -m rechtspraak_connector.cli test --config config/config.yaml

# 2) volledige run (handmatig):
python scripts/run_daily.py

# 3) automatiseren: zie scripts/crontab.example (cron of systemd-timer, 1×/nacht)
```

## Klaar voor AI (RAG / MCP), fase 2

Omdat `inhoud` schoon en losgekoppeld is van `metadata`, is de vervolgstap klein:
1. Activeer `pgvector` en de `uitspraak_chunks`-tabel (staat klaar in `schema.sql`).
2. Chunk `inhoud`, genereer embeddings, sla ze op met de `ecli` als sleutel.
3. Bouw een MCP-server of RAG-agent die **alleen** in deze eigen database zoekt —
   filteren op `rechtsgebieden`/`status='active'`, antwoorden met bronvermelding
   (ECLI + deeplink). Zo geen hallucinaties: de agent leest enkel jullie archief.

## Aannames / te verifiëren

- Endpoints en parameters volgen de officiële Rechtspraak Open Data-documentatie
  (`/uitspraken/zoeken` = Atom-feed met `return|max|from|sort|subject|creator|type|date|modified`;
  `/uitspraken/content?id=ECLI` = volledig document). Controleer de exacte
  **rechtsgebied-URI's** in de waardelijst:
  <https://data.rechtspraak.nl/Waardelijst/Rechtsgebieden>.
- "Ingetrokken/verwijderd" wordt gedetecteerd als de content-call 404 geeft of
  geen bruikbare metadata bevat. Pas `reconcile` aan als de Rechtspraak een
  expliciet intrekkings-signaal blijkt te leveren.
- Er wordt niets geüpload naar de Rechtspraak; de API is read-only (export).
