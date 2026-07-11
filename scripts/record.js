#!/usr/bin/env node
/*
 * record.js — render index.html to a 1080x1920 MP4 (Reels format).
 *
 * Drives the live animation in headless Chromium, captures PNG frames at a
 * fixed frame-rate while the presentation auto-plays through its scenes, then
 * encodes them to H.264 with ffmpeg. No cloud services, fully local.
 *
 * Usage:  node scripts/record.js [outfile.mp4]
 *
 * Deps (installed on demand, see README): playwright-core + an ffmpeg binary.
 * Resolves ffmpeg from @ffmpeg-installer/ffmpeg, ffmpeg-static, or $FFMPEG.
 */
const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawnSync } = require('child_process');

// ---- resolve chromium + ffmpeg (best-effort across environments) ----
function req(mod) { try { return require(mod); } catch { return null; } }
const playwright =
  req('playwright') || req('playwright-core') ||
  req('/opt/node22/lib/node_modules/playwright/node_modules/playwright-core');
if (!playwright) { console.error('playwright-core not found — npm i playwright-core'); process.exit(1); }
const { chromium } = playwright;

function findChromium() {
  if (process.env.CHROMIUM_PATH) return process.env.CHROMIUM_PATH;
  const roots = ['/opt/pw-browsers'];
  for (const r of roots) {
    if (!fs.existsSync(r)) continue;
    for (const d of fs.readdirSync(r)) {
      const p = path.join(r, d, 'chrome-linux', 'chrome');
      if (fs.existsSync(p)) return p;
    }
  }
  return undefined; // let playwright use its default
}
function findFfmpeg() {
  if (process.env.FFMPEG) return process.env.FFMPEG;
  const a = req('@ffmpeg-installer/ffmpeg'); if (a && a.path) return a.path;
  const b = req('ffmpeg-static'); if (b) return b;
  return 'ffmpeg';
}

// ---- config ----
const OUT = process.argv[2] || path.resolve('dist/omnichannel-architecture-1080x1920.mp4');
const FPS = 30;
const FILE = 'file://' + path.resolve(__dirname, '..', 'index.html');
const TRANSITION_MS = 1300; // camera ease (matches CSS 1.25s + margin)
const DWELL_MS = 3400;      // hold per scene after the camera settles

(async () => {
  const frameDir = fs.mkdtempSync(path.join(os.tmpdir(), 'frames-'));
  const browser = await chromium.launch({ executablePath: findChromium() });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto(FILE);
  await page.waitForFunction(() => typeof window.go === 'function');
  // take manual control of the timeline
  await page.evaluate(() => { window.setPlay(false); });
  const nScenes = await page.evaluate(() => document.querySelectorAll('#dots button').length);

  let frame = 0;
  const grab = async () => {
    await page.screenshot({ path: path.join(frameDir, String(frame).padStart(5, '0') + '.png') });
    frame++;
  };
  const captureFor = async (ms) => {
    const frames = Math.round((ms / 1000) * FPS);
    for (let i = 0; i < frames; i++) { await grab(); await page.waitForTimeout(1000 / FPS); }
  };

  for (let s = 0; s < nScenes; s++) {
    await page.evaluate((n) => window.go(n, true), s);
    await captureFor(TRANSITION_MS); // record the camera move + matrix rain
    await captureFor(DWELL_MS);      // hold on the scene
  }
  await browser.close();

  // ---- encode ----
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  const ff = findFfmpeg();
  console.log(`Encoding ${frame} frames @ ${FPS}fps -> ${OUT}`);
  const r = spawnSync(ff, [
    '-y', '-framerate', String(FPS),
    '-i', path.join(frameDir, '%05d.png'),
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
    '-vf', 'scale=1080:1920:flags=lanczos', '-r', String(FPS),
    '-movflags', '+faststart', '-crf', '20', '-preset', 'medium',
    OUT,
  ], { stdio: 'inherit' });
  fs.rmSync(frameDir, { recursive: true, force: true });
  if (r.status !== 0) { console.error('ffmpeg failed'); process.exit(1); }
  const mb = (fs.statSync(OUT).size / 1e6).toFixed(1);
  console.log(`Done: ${OUT} (${mb} MB, ${(frame / FPS).toFixed(1)}s)`);
})().catch(e => { console.error(e); process.exit(1); });
