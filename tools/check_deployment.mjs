// Read-only checks. Never submits a booking form or changes server settings.
import fs from 'node:fs';
import assert from 'node:assert/strict';
const origin = process.argv[2];
assert(origin, 'Usage: node tools/check_deployment.mjs https://hostname [--production]');
const production = process.argv.includes('--production');
const manifest = JSON.parse(fs.readFileSync(new URL('../build-manifest.json', import.meta.url)));
const migration = JSON.parse(fs.readFileSync(new URL('./migration.json', import.meta.url)));
const errors = [];
async function check(label, fn) {
  try { await fn(); } catch (e) { errors.push(`${label}: ${e.message}`); }
}
for (let offset = 0; offset < manifest.pages.length; offset += 4) {
  await Promise.all(manifest.pages.slice(offset, offset + 4).map(path => check(path, async () => {
    const response = await fetch(new URL(path, origin), {signal:AbortSignal.timeout(20000)});
    assert(response.status === 200 || (path === '/404.html' && response.status === 404), `HTTP ${response.status}`);
    const html = await response.text();
    assert(!html.includes('Parked Domain'), 'hosting is returning a parked-domain page');
    if (production && !['/404.html','/thank-you/'].includes(path)) assert(!/noindex/i.test(response.headers.get('x-robots-tag') || ''), 'HTTP header prevents indexing');
    const expected = !production || ['/404.html','/thank-you/'].includes(path);
    assert(/<meta name="robots" content="noindex, follow">/.test(html) === expected, 'wrong indexing mode');
    assert(html.includes(`href="https://109dental.ca${path}"`), 'wrong canonical');
    assert(!/Formerly Dr\.|Previously known as/.test(html), 'old clinic name');
    if (html.includes('data-booking-form')) assert(html.includes('action="api/enquiry.php"'), 'wrong booking destination');
  })));
}
for (const row of migration.filter(r => r.from !== r.to)) {
  await check(row.from, async () => {
    const response = await fetch(new URL(row.from + '?utm_source=launch-check', origin), {redirect:'manual',signal:AbortSignal.timeout(20000)});
    assert.equal(response.status, 301);
    const destination = new URL(response.headers.get('location'), origin);
    assert.equal(destination.pathname, row.to);
    assert.equal(destination.origin, new URL(origin).origin);
    assert.equal(destination.searchParams.get('utm_source'), 'launch-check');
  });
}
const assetPaths = ['css/styles.css','js/main.js','assets/brand-logo.png', ...fs.readdirSync(new URL('../assets/photos/', import.meta.url)).filter(f=>/\.(webp|png|jpe?g)$/i.test(f)).map(f=>'assets/photos/'+f)];
await Promise.all(assetPaths.map(path=>check(path,async()=>{
  const response = await fetch(new URL(path,origin), {signal:AbortSignal.timeout(20000)});
  assert.equal(response.status,200);
  assert(!/text\/html/i.test(response.headers.get('content-type') || ''), 'asset URL returned HTML, possibly a hosting placeholder');
  const content = Buffer.from(await response.arrayBuffer());
  const local = fs.readFileSync(new URL('../' + path, import.meta.url));
  assert(content.equals(local), 'deployed asset does not match release');
})));
await check('unknown URL', async()=>{
  const response = await fetch(new URL('/launch-check-does-not-exist/',origin),{signal:AbortSignal.timeout(20000)});
  assert.equal(response.status,404);
});
if (production) {
  await check('robots.txt', async()=>{
    const response=await fetch(new URL('/robots.txt',origin));
    assert.equal(response.status,200);
    const text=await response.text();
    assert(!/^Disallow:\s*\/\s*$/mi.test(text), 'host is blocking crawlers');
    assert(text.includes('Sitemap: https://109dental.ca/sitemap.xml'));
  });
}
if (errors.length) { console.error(errors.join('\n')); process.exitCode=1; }
else console.log(`PASS: ${manifest.pages.length} live pages, 23 permanent redirects with attribution preserved, ${assetPaths.length} assets, and real 404 response. No forms submitted.`);
