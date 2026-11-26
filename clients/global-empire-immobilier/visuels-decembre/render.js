// Rend chaque <section class="s"> de visuels.html en PNG 1080x1350 dans ./png/
const {chromium} = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const dir = __dirname, out = path.join(dir, 'png');
  fs.mkdirSync(out, {recursive: true});
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 1080, height: 1350}, deviceScaleFactor: 1});
  await p.goto('file://' + path.join(dir, 'visuels.html'), {waitUntil: 'networkidle'});
  await p.evaluate(() => document.fonts.ready);
  for (const el of await p.$$('section.s')) {
    const name = await el.getAttribute('data-name');
    await el.screenshot({path: path.join(out, name + '.png')});
  }
  await b.close();
})();
