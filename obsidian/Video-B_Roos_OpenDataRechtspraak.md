---
title: "Video B — Roos: Open Data Rechtspraak (walk & explain)"
type: video-productie
project: Recruitin / Gelre — uitlegvideo
status: final
aspect: "16:9"
duur: "~32s (final v3)"
stem: "Roos (voice-clone)"
datum: 2026-07-12
tags: [video, rechtspraak, ecli, roos, voice-over, higgsfield]
---

# Video B — Roos: Open Data Rechtspraak

> [!success] Finale render (Roos-stem, ElevenLabs-engine)
> https://d8j0ntlcm91z4.cloudfront.net/user_3D6jAHOHLxxvsiq5soyxcSoPg98/hf_20260712_111605_4af26b59-1846-4b7e-a2ce-5f3a6c237367.mp4

16:9 explainer, ~30s, 6 scènes. Roos loopt door een modern advocatenkantoor en
legt uit hoe je via **Open Data Rechtspraak** met het **ECLI-nummer** uitspraken vindt.

## Stem (voice-over)

| Veld | Waarde |
|------|--------|
| Voice-element | **Roos-1** |
| Higgsfield voice_id | `1f7dd884-92e8-4f22-8c44-d799d3e2632a` (type `element`) |
| Bron | voice-clone uit `Roos_stem_sample_45s.mp3` (via create_voice widget) |
| TTS-engine | `text2speech_v2` · variant **`elevenlabs`** (goede NL-uitspraak, server-side) |
| Let op | `seed_audio`-clone gaf slechte NL-uitspraak → **niet** gebruiken; ElevenLabs-engine wel |

> [!note] Waarom niet de directe ElevenLabs-API
> `api.elevenlabs.io` is in de sandbox geblokkeerd (egress-policy 403). De
> ElevenLabs-engine draait wél via Higgsfield's `text2speech_v2`. Voor de exacte
> productie-stem `7qdUFMklKPaaAVMsBTBt` kan de VO op een eigen machine gedraaid
> worden en als losse mp3's ingemonteerd.

## VO-scripts (6 scènes, ~5s elk)

1. Elke rechterlijke uitspraak in Nederland is openbaar, en ik laat je precies zien hoe.
2. Al die uitspraken staan gewoon gratis online, via de Open Data van de Rechtspraak.
3. Elke uitspraak heeft één uniek kenmerk, en dat noemen we het ECLI-nummer.
4. Met dat ene nummer vind je in drie simpele stappen precies de juiste zaak.
5. Geen dikke wetboeken meer nodig: alles is doorzoekbaar met slechts één muisklik.
6. Zo werkt Open Data Rechtspraak: slimmer zoeken, en veel sneller een antwoord.

> [!tip] Timing-fix voor flow
> Korte VO wordt door de montage in een vast 5s-blok **gecentreerd** → stilte
> rond de zin → hoorbare pauze na de cut. Oplossing: elke take op **~4,5–5s**
> houden zodat hij het blok vult. Bovenstaande zinnen zijn hierop afgestemd.

## Assets (Higgsfield job-IDs)

### Keyframes (16:9, soul_2, Roos `82f27f82-5700-4d73-b398-199ee285c206`)
| # | Scène | Keyframe-ID |
|---|-------|-------------|
| 1 | hal, glaswanden | `9302d987-c459-414d-aef8-7aee303a5ade` |
| 2 | glaswand + data-dashboards | `8a74fd37-fa01-4d04-a4c1-09c50ba00747` |
| 3 | open werkvloer, laptops | `06aebd6c-92a9-44b5-8d1b-3f34629aff9c` |
| 4 | 3-stappen-scherm | `e02f7497-9d7e-4dd3-8f8c-952a8d86e4f7` |
| 5 | boeken-/archiefwand | `555df097-bc7a-40e1-908e-39a194bb25dc` |
| 6 | bureau-aankomst | `8ae1a540-8be6-42a8-b8fc-9ea63ee0b06e` |
| 7 | CTA, camera-frontaal | `82cddf00-936b-4258-a898-46d25aee6e85` |

### Walk-clips (kling3_0 dual-keyframe, 16:9, 5s, silent)
| # | Overgang | Clip-ID | VO-take (elevenlabs) |
|---|----------|---------|----------------------|
| 1 | kf1→kf2 | `5b498fc6-737e-4e91-882e-52961d12b43b` | `133b9911-ae60-43e6-80fa-dbdda2b73322` |
| 2 | kf2→kf3 | `0be107c3-0cec-4772-81db-5947d76dc0ae` | `f6a24607-07d5-4829-9805-9f8aa0c33ba0` |
| 3 | kf3→kf4 | `1e86531a-b436-4192-bdfe-9179e526eef0` | `6e5e757d-bb7e-48f8-9eaf-00b500da92e5` |
| 4 | kf4→kf5 | `f6122432-1780-4aeb-911c-20c2647bcd97` | `ed30d2b7-8c88-47f2-96ae-c5b21559d84a` |
| 5 | kf5→kf6 | `103117b5-8e2e-4310-9238-eb1be3c525c6` | `ef49bdd2-add1-45bc-ba9e-a0347d10a32f` |
| 6 | kf6→kf7 | `06e1f67c-c29c-46f6-b86e-9269d30ae59f` | `85e1e8ce-df64-483c-bb2b-56e16b931717` |

Montage: `explainer_video` · 1280×720 · job `4af26b59-1846-4b7e-a2ce-5f3a6c237367`.

## Kosten (Higgsfield credits)
- 7 keyframes (soul_2) + 6 clips × 7,5 + VO-takes (elevenlabs) → ~55 cr totaal.

## Finale montage — v3 (opgelost)
> [!success] Definitieve versie
> **Overgangen + VO-timing lokaal met ffmpeg opgelost** (clips via Drive→zip→chat op schijf).

Pipeline (lokaal, `imageio-ffmpeg` 7.0.2 wegens `xfade`):
1. **Crossfades**: 6 clips met `xfade=transition=dissolve:duration=0.5` (dip-to-black `fadeblack` en 0,8s dissolve waren tussenvarianten).
2. **Scènes vertraagd ~15%** (`setpts=1.15*PTS`) → elke scène ~5,8s, zodat de VO ademruimte krijgt.
3. **VO sequentieel** op de scène-starts (0 · 5,3 · 10,6 · 15,9 · 21,2 · 26,5s) via `adelay`+`amix=normalize=0` → geen overlap, korte stilte-pauze na elke zin vóór de dissolve.
4. Video `-c:v copy`, audio AAC 192k, `alimiter`. Eindduur **32,3s**.

Iteraties (feedback → fix):
- harde cut → glitch → **crossfade** (beter);
- dissolve-glitch → **fadeblack / langere dissolve** (B gekozen);
- VO-overlap ("2e start als 1e nog draait") → **sequentiële VO** (0,5s dissolve);
- geen adempauze → **scènes 15% vertraagd + gap** (v3, akkoord).

> [!note] Nog strakker? DaVinci Resolve
> Voor een échte optical-flow morph over de Kling-cliprand: DaVinci "Smooth Cut" +
> Retime → Optical Flow. Assets (6 clips + `roos_vo_1..6.mp3`) staan in de Drive-map.

## Reproduceren
1. Voice-element **Roos-1** bestaat al (`1f7dd884-…`); anders opnieuw clonen via create_voice (upload-tab, sample `Roos_stem_sample_45s.mp3`).
2. Per scène: `generate_audio` → `text2speech_v2`, variant `elevenlabs`, `voice_type: element`, `voice_id: 1f7dd884-…`, prompt = scriptregel.
3. `explainer_video` · 1280×720 · items = 6× `{video: clip-ID, audio: vo-ID}` in volgorde.

## Zie ook
- [[explainer-ecli]] — Gelre-huisstijl ECLI-explainer
- [[rechtspraak-connector]] — Open Data Rechtspraak API-connector
