import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const inline = html.match(/<script>([\s\S]*?)<\/script>/)[1];
for (const [url, expected] of [
  ['https://stockwise-support.github.io/109-dental-site/services/wisdom-teeth/', 'https://stockwise-support.github.io/109-dental-site/'],
  ['https://palevioletred-ant-543523.hostingersite.com/services/wisdom-teeth/', 'https://palevioletred-ant-543523.hostingersite.com/'],
  ['https://109dental.ca/about/', 'https://109dental.ca/'],
  ['http://127.0.0.1:8099/about/', 'http://127.0.0.1:8099/'],
  ['https://stockwise-support.github.io/109-dental-review/services/wisdom-teeth/', 'https://stockwise-support.github.io/109-dental-review/'],
]) {
  const base = {href:''};
  vm.runInNewContext(inline, {location:new URL(url),document:{querySelector:()=>base}});
  assert.equal(base.href, expected, url);
  assert.equal(new URL('assets/brand-logo.png',base.href).href,expected+'assets/brand-logo.png');
}
console.log('PASS: root-domain, main/review GitHub subpaths, and localhost base paths.');
