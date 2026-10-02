import { chromium } from 'playwright';
import fs from 'fs';
const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
const urls = JSON.parse(fs.readFileSync('../lm/pages.json')).map(p => p.url);
const out = [];
const one = async url => {
  const p = await ctx.newPage();
  try {
    await p.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
    out.push(await p.evaluate(u => {
      const vis = e => e && e.offsetParent && !/Cookie/.test(e.innerText) && !e.closest('nav,header,footer') && !e.classList.contains('v');
      const q = s => [...document.querySelectorAll(s)].filter(vis);
      const h1 = q('h1')[0];
      const txt = e => e ? e.innerText.trim().replace(/\s+/g, ' ') : '';
      const sub = q('h2.m0')[0] || (h1 && h1.nextElementSibling?.tagName === 'H4' ? h1.nextElementSibling : null);
      const para = q('p').map(txt).find(t => t.length > 80 && !/Accesskey/.test(t)) || '';
      const img = [...document.querySelectorAll('img')].map(i => i.getAttribute('src') || '').find(s => /\/media\/image\/.*\/\d+\.jpg/.test(s)) || '';
      return { url: u, doctitle: document.title, cat: txt(q('p.cat')[0]), title: txt(h1), sub: txt(sub), when: txt(q('p.eventdate')[0] || q('p.precontent-p')[0]), para, img };
    }, url));
  } catch (e) { console.log('fail', url, e.message.slice(0, 80)); }
  await p.close();
};
for (let i = 0; i < urls.length; i += 4) await Promise.all(urls.slice(i, i + 4).map(one));
fs.writeFileSync('../lm/pages3.json', JSON.stringify(out, null, 1));
console.log('scraped', out.length);
await b.close();
