import fs from 'node:fs';
import assert from 'node:assert/strict';
const root = new URL('../', import.meta.url);
const manifest = JSON.parse(fs.readFileSync(new URL('build-manifest.json', root), 'utf8'));
for (const prefix of ['https://109dental.ca/', 'https://palevioletred-ant-543523.hostingersite.com/', 'http://127.0.0.1:8099/', 'https://stockwise-support.github.io/109-dental-site/']) {
  for (const path of manifest.pages) {
    if(path === '/404.html') continue;
    const file = path.slice(1) + 'index.html';
    const html = fs.readFileSync(new URL(file, root), 'utf8');
    const base = html.match(/<base href="([^"]+)"/)[1];
    const resolved = new URL(base, prefix + path.slice(1)).href;
    assert.equal(resolved, prefix, path);
    assert.equal(new URL('css/styles.css',resolved).href, prefix+'css/styles.css');
  }
}
console.log('PASS: every content page resolves assets and links without JavaScript on root domains and subpaths.');
