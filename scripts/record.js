#!/usr/bin/env node
/*
 * record.js — render index.html to a 1080x1920 MP4 (Reels format).
 *
 * Uses Playwright's native video capture (no per-frame screenshots) to record
 * the live presentation as it plays through every scene, then transcodes the
 * WebM to H.264 MP4 with ffmpeg. Fully local, no cloud services.
 *
 * Usage:  node scripts/record.js [outfile.mp4]
 *
 * Resolves ffmpeg from $FFMPEG, @ffmpeg-installer/ffmpeg, or ffmpeg-static.
 */
const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawnSync } = require('child_process');

function req(mod) { try { return require(mod); } catch { return null; } }
const playwright =
  req('playwright') || req('playwright-core') ||
  req('/opt/node22/lib/node_modules/playwright/node_modules/playwright-core');
if (!playwright) { console.error('playwright-core not found — npm i playwright-core'); process.exit(1); }
const { chromium } = playwright;

function findChromium() {
  if (process.env.CHROMIUM_PATH) return process.env.CHROMIUM_PATH;
  const root = '/opt/pw-browsers';
  if (fs.existsSync(root)) {
    for (const d of fs.readdirSync(root)) {
      const p = path.join(root, d, 'chrome-linux', 'chrome');
      if (fs.existsSync(p)) return p;
    }
  }
  return undefined;
}
function findFfmpeg() {
  if (process.env.FFMPEG) return process.env.FFMPEG;
  const a = req('@ffmpeg-installer/ffmpeg'); if (a && a.path) return a.path;
  const b = req('ffmpeg-static'); if (b) return b;
  return 'ffmpeg';
}

const W = 1080, H = 1920, FPS = 30;
const OUT = process.argv[2] || path.resolve('dist/omnichannel-architecture-1080x1920.mp4');
const FILE = 'file://' + path.resolve(__dirname, '..', 'index.html');
const TRANSITION_MS = 1300;  // camera ease (matches CSS 1.25s + margin)
const DWELL_MS = 3400;       // hold per scene once the camera settles

(async () => {
  const vidDir = fs.mkdtempSync(path.join(os.tmpdir(), 'vid-'));
  const browser = await chromium.launch({ executablePath: findChromium() });
  const context = await browser.newContext({
    viewport: { width: W, height: H },
    recordVideo: { dir: vidDir, size: { width: W, height: H } },
  });
  const page = await context.newPage();
  await page.goto(FILE);
  await page.waitForFunction(() => typeof window.go === 'function');
  await page.evaluate(() => window.setPlay(false)); // drive the timeline ourselves
  const n = await page.evaluate(() => document.querySelectorAll('#dots button').length);

  for (let s = 0; s < n; s++) {
    await page.evaluate((i) => window.go(i, true), s);
    await page.waitForTimeout(TRANSITION_MS + DWELL_MS);
  }

  await context.close(); // finalizes the .webm
  await browser.close();

  const webm = fs.readdirSync(vidDir).find(f => f.endsWith('.webm'));
  if (!webm) { console.error('no video captured'); process.exit(1); }
  const webmPath = path.join(vidDir, webm);

  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  const ff = findFfmpeg();
  console.log(`Transcoding ${webm} -> ${OUT}`);
  const r = spawnSync(ff, [
    '-y', '-i', webmPath,
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
    '-vf', `scale=${W}:${H}:flags=lanczos,fps=${FPS}`,
    '-movflags', '+faststart', '-crf', '20', '-preset', 'medium',
    OUT,
  ], { stdio: 'inherit' });
  fs.rmSync(vidDir, { recursive: true, force: true });
  if (r.status !== 0) { console.error('ffmpeg failed'); process.exit(1); }
  const mb = (fs.statSync(OUT).size / 1e6).toFixed(1);
  console.log(`Done: ${OUT} (${mb} MB)`);
})().catch(e => { console.error(e); process.exit(1); });
