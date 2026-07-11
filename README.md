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

## Voice-over script (NL, resultaat-gedreven — voor de niet-technische beslisser)

De VO is bewust omgebouwd van *techniek-uitleg* naar *wat het oplevert*, in
gewone taal en geruststellend van toon — gericht op een HR-manager of
bureau-eigenaar, niet op een systeemarchitect. Twee sprekers:

1. **Neo-hook** (diepe, trage stem) over de intro-scène — de scroll-stopper.
   > Welcome… to the Matrix… of the AI-OS recruitment system.
2. **Nederlandse narratie** (Orion, ± 1:34) — start zodra de muur afbrokkelt en
   loopt door t/m het vliegwiel. Opent met een resultaat-hook, daarna één
   duidelijke belofte per scène.

**Hook — bij de reveal** *(nieuwsgierig)*
> Wat als één druk op de knop je hele week aan recruitment-content oplevert?
> Automatisch. En jij houdt altijd de controle.

**Eén scan** — *0 blanco pagina's*
> Het begint met één wekelijkse scan van jouw vakgebied. Meer hoef jij niet te
> doen; het systeem weet al hoe jouw merk klinkt, en waar jouw doelgroep op zit.

**Vanuit één plek** — *geen los geknutsel*
> Eén centrale regisseur plant en bewaakt het hele proces. Jij hoeft niets te
> koppelen of in de gaten te houden.

**Slim én zuinig** — *tot 90% goedkoper*
> Voor elke taak kiest het systeem automatisch het beste én goedkoopste model.
> Zware klussen slim, simpele klussen goedkoop. Jij betaalt nooit te veel.

**Tekst én beeld** — *geen aparte designer nodig*
> Het bekijkt de concurrentie, en maakt de teksten, beelden en video's er meteen
> bij. Alles kant-en-klaar, in jouw huisstijl.

**Eén onderwerp, vier kanalen** — *4× bereik, 0 kopieerwerk*
> Uit dat ene onderwerp maakt het systeem vier unieke versies: voor je website,
> voor LinkedIn, en voor je advertenties. Nooit gekopieerd.

**LinkedIn dual-track** — *5–10× meer weergaven*
> Op LinkedIn plaatst het slim vanaf je bedrijfspagina én je persoonlijke
> profiel. Zo bereik je veel meer mensen, zonder gedoe.

**On-brand & compliant** — *geen missers online*
> Voordat er iets naar buiten gaat, controleert het systeem de kwaliteit, je
> huisstijl, en de nieuwste regels van LinkedIn en Meta. Zo staat er nooit een
> misser online.

**Jij beslist** — *de mens beslist, niet de AI*
> En het allerbelangrijkste: niets gaat live zonder jouw akkoord. Jij houdt de
> eindcontrole.

**Het resultaat** — *ruim 20 uur per week terug*
> Eén scan wordt jouw hele week aan content, op elk kanaal. Je wint zo'n twintig
> uur per week. En je blijft continu zichtbaar, bij de juiste mensen.

De schermtekst (`title` + oranje `res`-metric per scène in `SCENES`) loopt
één-op-één mee met deze VO. De narratie (± 94s) valt over de architectuur-scènes;
pas een zin aan, zet de bijbehorende `dur` gelijk, en re-render.

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
`dur` gelijk, en re-render. De huidige set (cinematische intro 23,5s +
architectuur 90s + cliffhanger 8s) geeft ± 2:01 totaal, strak op de ± 1:46 VO.
Valt `SCENE_DUR` weg, dan gebruikt de recorder de vaste `TRANSITION_MS +
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
