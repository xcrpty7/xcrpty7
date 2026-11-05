// Render exact animation frames of one SVG (CSS + SMIL frozen at the given seconds).
// Usage: node scripts/frames.js <file.svg> <out_prefix> <t1,t2,...> [device_scale]
// Needs playwright-core and a downloaded Chromium; set PW_CORE to its path if it is not resolvable,
// e.g. PW_CORE=~/.hermes/hermes-agent/node_modules/playwright-core
// Live <img> previews are unreliable for this: Chrome does not advance SVG animations off screen.
const path = require('path');

function playwright() {
  try { return require('playwright-core'); } catch (_) { /* fall through */ }
  if (process.env.PW_CORE) return require(path.resolve(process.env.PW_CORE.replace(/^~/, process.env.HOME)));
  throw new Error('playwright-core not found: npm i -D playwright-core, or set PW_CORE');
}

(async () => {
  const [svgPath, out, times, scale] = process.argv.slice(2);
  if (!svgPath || !out || !times) throw new Error('usage: node scripts/frames.js <file.svg> <out_prefix> <t1,t2,...> [scale]');
  const browser = await playwright().chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: Number(scale || 1) });
  await page.goto(`file://${path.resolve(svgPath)}`);
  const size = await page.evaluate(() => {
    const vb = document.documentElement.viewBox.baseVal;
    return { width: Math.ceil(vb.width), height: Math.ceil(vb.height) };
  });
  await page.setViewportSize(size);
  for (const t of times.split(',').map(Number)) {
    await page.evaluate(sec => {
      document.documentElement.pauseAnimations();
      document.documentElement.setCurrentTime(sec);
      for (const a of document.getAnimations()) { a.pause(); a.currentTime = sec * 1000; }
    }, t);
    await page.waitForTimeout(80);
    const file = `${out}-${String(t).replace('.', '_')}s.png`;
    await page.screenshot({ path: file });
    console.log(file);
  }
  await browser.close();
})().catch(err => { console.error(`frames: ${err.message}`); process.exit(1); });
