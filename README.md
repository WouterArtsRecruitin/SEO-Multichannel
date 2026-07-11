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

Open `index.html` in een browser. De presentatie is één bestand (HTML + CSS +
vanilla JS + canvas Matrix-rain); de enige externe asset is het Recruitin-logo
in `assets/recruitin-mark.png`, dus houd de map `assets/` naast `index.html`.
Er is een gebrande **intro** (logo-reveal) en **outro** ("Welkom in de matrix").

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

| Laag | Node(s) | Rol |
|------|---------|-----|
| **0. Bron & trigger** | Recruitment-Monitor · Cloud Trigger (+ custom input-MCP) | Wekelijkse scan van recruitment-updates → payload (.json/.md); webhook/cronjob start-signaal |
| **1. Kennis / SSOT** | Obsidian Vault | Instructies v5 · tone of voice · buyer persona's · SEO-pijlers · templates (SSOT), gelezen als YAML |
| **2. Orkestratie** | Content Orchestrator (eigen workflow-engine) | Centrale cloud-workflows · content-planner · state manager |
| **3. Model-router** | LiteLLM Router → Claude Haiku / Sonnet 5 / Gemini 3.1 Pro | Leest YAML, kiest per taak het juiste én goedkoopste model (triage / code & copy / grote datasets) → executie-fase |
| **4. Research & media** | Apify SERP · Leonardo · Kling · Placid/Bannerbear · Midjourney · Supabase | Concurrentie-scrape, beeld & video, corporate/candid visuals, concept samenvoegen & status-DB |
| **5. Omnichannel-splitsing** | SEO Blog-Writer · LinkedIn Bedrijf (Route A) · LinkedIn Persoonlijk (Route B) · Meta Ad Copywriter | Eén onderwerp → vier unieke kanaalversies; LinkedIn **dual-track** omzeilt de straf op dubbele content |
| **6. Kwaliteit, merk & AIA** | Interne Kwaliteits-Sluis · Brand Guardian + Compliance Counsel · Algorithm Intelligence Agent | AI SEO-check; huisstijl & compliance; realtime immuunsysteem tegen algoritme-wijzigingen |
| **7. Menselijke sluis** | Cowork Wait-State | Orchestrator pauzeert tot de redacteur goedkeurt |
| **8. Publicatie + vliegwiel** | WordPress/Webflow · LinkedIn API (Buffer/ShareIn) · Meta Marketing API | Live/ingepland; feedback-loop (statusupdate) terug naar de orchestrator = autonoom vliegwiel |

**Agent-skills** zichtbaar in de animatie: SEO Blog-Writer — `generate_seo_structure()`,
`create_internal_links()`; Algorithm Intelligence Agent — `update_platform_guidelines()`,
`audit_algorithm_match()`.

De oranje gestippelde lijn is de **feedback-loop**: statusupdates stromen vanuit
de publicatie terug naar de orchestrator — het autonome vliegwiel. Gloeiende
data-pakketjes lopen over elke verbinding mee (incl. de feedback-kabel terug).

## Voice-over script (NL, je/jouw-vorm)

De ondertitels in de animatie zijn tegelijk het VO-script. Geschikt voor een
ElevenLabs-avatar; totale spreektijd ± 80 seconden, verdeeld over 7 blokken die
één-op-één met de scènes (en hun schermtijd) overeenkomen — zie de duur per
scène in `window.SCENE_DUR` bovenaan het script. Regie-aanwijzing per scène
tussen haakjes.

**Intro — Recruitin · AI Agency** *(hook, mysterieus)* — ± 8s
> Wat als één brononderwerp automatisch je hele contentmachine voedt? Dit is het
> Omnichannel AI Content OS van Recruitin.

**Scene 1 — De Bron & Orkestratie** *(rustig, opbouwend)*
> Alles start bij de bron. Jouw wekelijkse recruitment-scan stroomt als data
> direct de Centrale Content Planner binnen. De Obsidian Vault
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

## Video-export (MP4) — voor ElevenLabs / CapCut

`scripts/record.js` rendert de animatie naar een kant-en-klare **1080×1920 H.264 MP4**
(Reels-formaat) die je naast de ElevenLabs voice-over kunt leggen. Playwright speelt
de live-animatie af en legt frames vast; ffmpeg codeert ze tot een MP4.

```bash
# eenmalig: dependencies
npm install                       # playwright-core + @ffmpeg-installer/ffmpeg
npx playwright install chromium   # of laat CHROMIUM_PATH wijzen naar een bestaande build

# renderen -> dist/omnichannel-architecture-1080x1920.mp4
node scripts/record.js [uitvoer.mp4]
```

De schermtijd per scène komt uit `window.SCENE_DUR` in `index.html` (seconden),
zodat video en voice-over exact gelijk lopen: pas een VO-zin aan, zet de bijbehorende
`dur` gelijk, en re-render. De huidige set (8-13-13-10-14-14-14s) geeft ± 86s
totaal. Valt `SCENE_DUR` weg, dan gebruikt de recorder de vaste `TRANSITION_MS +
DWELL_MS` bovenaan `scripts/record.js`. De MP4 heeft geen audio — de voice-over
leg je eronder in je editor of ElevenLabs.

## Aanpassen

Alle content zit bovenaan het `<script>`-blok in `index.html`:

- **`NODES`** — voeg nodes toe/wijzig tekst, kleur, icoon en positie (`x,y,w,h`
  in wereldcoördinaten, canvas is 1080 breed).
- **`WIRES`** — verbindingen tussen node-id's; `{feedback:true}` maakt een
  oranje gestippelde loop, `{lab:'...'}` zet een label op de lijn.
- **`SCENES`** — camera (`cx,cy,sc`), welke nodes oplichten (`on`) en de VO-tekst.
- **`SCENE_MS`** — duur per scène bij autoplay.
