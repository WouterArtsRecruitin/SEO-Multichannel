# Omnichannel AI Agency — Geanimeerde Architectuur

Een **self-contained**, geanimeerde node-based presentatie van de volledige
Omnichannel Content OS architectuur van Recruitin. Eén HTML-bestand, geen
build-step, geen dependencies, geen CDN's — direct deploybaar op Netlify vanaf
de repo-root.

De presentatie is opgebouwd in **Reels-formaat (1080×1920)** met een dark-neon
"consultancy" thema en een custom **Matrix digital rain** achtergrond. Een
virtuele camera beweegt vloeiend (Smart-Animate-stijl, ease-out) door zes
scènes die samen de complete procesflow van A tot Z tonen.

## Bekijken

Open `index.html` in een browser. Meer is niet nodig — alles zit in dat ene
bestand (HTML + CSS + vanilla JS + canvas Matrix-rain).

**Bediening**
- `▶ / ⏸` — autoplay aan/uit (8,2s per scène)
- `←` `→` — vorige / volgende scène
- `spatie` — play/pauze
- de bolletjes onderaan springen direct naar een scène

## Deployen op Netlify

Static site, geen build. `netlify.toml` staat al klaar:

1. Koppel deze repo aan een nieuw Netlify-project (of sleep de map naar
   Netlify Drop).
2. Publish directory = `.` (root), build command = leeg.
3. Klaar — `index.html` wordt de landingspagina.

## De architectuur (van A tot Z)

| Fase | Node(s) | Rol |
|------|---------|-----|
| **1. Bron** | Recruitment-Monitor · Obsidian Vault | Wekelijkse data-scan (.json) + merkstem/SEO-pijlers/templates als single source of truth |
| **2. Orkestratie** | Google Stitch | Centrale Content Planner / cloud-orkestrator & state manager |
| **3. Routing** | LiteLLM Router → Claude Haiku / Claude Sonnet 5 / Gemini 3.1 Pro | Leest Obsidian-YAML en kiest per taak het juiste model (triage / copy / long-form) |
| **3b. Tools & data** | Apify · Leonardo/Kling · Supabase | SERP-scrape, media-generatie, concept samenvoegen & opslaan |
| **4. Omnichannel splitsing** | SEO Blog-Writer · LinkedIn Bedrijf · LinkedIn Persoonlijk · Meta Ad Copywriter | Eén brononderwerp → vier unieke kanaalversies |
| **5. Sluis** | Brand & Compliance · Algorithm Intelligence Agent · Cowork Wait-State | Huisstijl-check, live algoritme-check (Meta/LI) en menselijke goedkeuring |
| **6. Publicatie** | Omnichannel Out | WordPress · LinkedIn · Meta · Buffer — plus feedback-loop terug naar Stitch |

De oranje gestippelde lijn is de **feedback-loop**: statusupdates stromen vanuit
de publicatie terug naar Google Stitch — het autonome vliegwiel.

## Voice-over script (NL, je/jouw-vorm)

De ondertitels in de animatie zijn tegelijk het VO-script. Geschikt voor een
ElevenLabs-avatar; totale spreektijd ± 55–65 seconden. Regie-aanwijzing per
scène tussen haakjes.

**Scene 1 — De Bron & Orkestratie** *(rustig, opbouwend)*
> Alles start bij de bron. Jouw wekelijkse recruitment-scan stroomt als data
> direct de Centrale Content Planner — Google Stitch — binnen. De Obsidian Vault
> levert merkstem, SEO-pijlers en templates als single source of truth.

**Scene 2 — De Dynamische Model Router** *(technisch, zelfverzekerd)*
> De Router leest de Obsidian-YAML en kiest per taak het juiste brein: Claude
> Haiku voor snelle triage, Claude Sonnet 5 voor precieze copy en code, en
> Gemini 3.1 Pro voor long-form en grote datasets.

**Scene 3 — Research, Media & Opslag** *(vlot)*
> Parallel scrapt Apify de top-10 concurrenten, genereert Leonardo de beelden,
> en voegt Supabase alle losse elementen samen tot één compleet concept-artikel.

**Scene 4 — De Omnichannel Splitsing** *(enthousiast — de climax van de flow)*
> Hier gebeurt de magie: één brononderwerp wordt uniek opgesplitst. Een SEO-blog
> voor je website, een B2B-carrousel voor je bedrijfspagina, een persoonlijk
> verhaal voor je profiel én actiegerichte Meta Ads.

**Scene 5 — Compliance & Algorithm Intelligence** *(krachtig, geruststellend)*
> Voordat er iets live gaat bewaakt de Brand Guardian je huisstijl, en scant de
> Algorithm Intelligence Agent realtime de regels van Meta en LinkedIn. Daarna
> wacht het systeem op jouw akkoord in de Cowork-sluis.

**Scene 6 — Publicatie & Het Vliegwiel** *(uitnodigend, zoomt uit)*
> Na goedkeuring publiceert het systeem volautomatisch naar al je kanalen. Het
> resultaat: een autonoom, omnichannel vliegwiel dat 24/7 jouw autoriteit bouwt
> en leads converteert. Welkom in de matrix.

**ElevenLabs-tip:** stem met hoge autoriteit maar conversationele toon (bijv.
Callum of Marcus), Stability ± 35%. Forceer pauzes tussen scènes met
`<break time="1.0s" />` om de VO exact op de camera-overgangen te synchroniseren.

## Aanpassen

Alle content zit bovenaan het `<script>`-blok in `index.html`:

- **`NODES`** — voeg nodes toe/wijzig tekst, kleur, icoon en positie (`x,y,w,h`
  in wereldcoördinaten, canvas is 1080 breed).
- **`WIRES`** — verbindingen tussen node-id's; `{feedback:true}` maakt een
  oranje gestippelde loop, `{lab:'...'}` zet een label op de lijn.
- **`SCENES`** — camera (`cx,cy,sc`), welke nodes oplichten (`on`) en de VO-tekst.
- **`SCENE_MS`** — duur per scène bij autoplay.
