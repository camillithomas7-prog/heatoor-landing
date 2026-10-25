"""Rende la pagina a prova di builder CheckoutChamp (GrapesJS).

Il builder fonde le regole con lo stesso selettore, perde le custom property
negli style inline e scarta il <link> dei font. Qui, in un vero browser:
- gli style inline diventano classi .ix-N con !important
- tutte le var(--x) vengono sostituite con il valore reale
- ogni selettore (anche dentro le liste con virgola) compare una sola volta
- body / #product-page-v8 diventano il wrapper .pp-root
- i font sono @font-face ospitati su GitHub Pages
"""
import asyncio, sys, os
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = 'https://camillithomas7-prog.github.io/heatoor-landing/assets/'
FACES = [('Roboto', 400, 'Roboto-Regular'), ('Roboto', 500, 'Roboto-Medium'), ('Roboto', 600, 'Roboto-SemiBold'),
         ('Roboto', 700, 'Roboto-Bold'), ('Roboto', 800, 'Roboto-ExtraBold'), ('Roboto', 900, 'Roboto-Black'),
         ('Poppins', 400, 'Poppins-Regular'), ('Poppins', 500, 'Poppins-Medium'), ('Poppins', 600, 'Poppins-SemiBold'),
         ('Poppins', 700, 'Poppins-Bold'), ('Poppins', 800, 'Poppins-ExtraBold')]

JS = r'''() => {
  const vars = {};
  const grab = st => { for (let i = 0; i < st.length; i++) { const p = st[i]; if (p.startsWith('--')) vars[p] = st.getPropertyValue(p).trim(); } };
  // 1) style inline -> classi
  let n = 0; const inlineRules = [];
  document.querySelectorAll('[style]').forEach(el => {
    const st = el.style; grab(st);
    const decl = [];
    for (let i = 0; i < st.length; i++) { const p = st[i]; if (!p.startsWith('--')) decl.push(p + ':' + st.getPropertyValue(p) + ' !important'); }
    el.removeAttribute('style');
    if (decl.length) { const c = 'ix-' + (++n); el.classList.add(c); inlineRules.push(['', '.' + c, decl.join(';')]); }
  });
  // 2) raccolta regole
  const rules = []; const keep = [];
  const splitSel = s => { const out = []; let d = 0, cur = ''; for (const ch of s) { if (ch === '(' ) d++; if (ch === ')') d--; if (ch === ',' && !d) { out.push(cur.trim()); cur = ''; } else cur += ch; } out.push(cur.trim()); return out; };
  const walk = (list, media) => { for (const r of list) {
    if (r.type === 1) { grab(r.style);
      if (/^(:root|html|body|#product-page-v8)$/.test(r.selectorText.trim()) === false || true) rules.push([media, r.selectorText, r.style.cssText]);
    } else if (r.type === 4) walk(r.cssRules, r.conditionText || r.media.mediaText);
    else if (r.type === 7 || r.type === 12) keep.push(r.cssText);
  } };
  for (const s of document.styleSheets) { try { walk(s.cssRules, ''); } catch (e) {} }
  for (const r of inlineRules) rules.push(r);
  const resolve = v => { for (let k = 0; k < 8 && v.includes('var('); k++)
    v = v.replace(/var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*(?:\([^()]*\)[^()]*)*))?\)/g, (m, name, fb) => vars[name] !== undefined ? vars[name] : (fb !== undefined ? fb.trim() : 'initial')); return v; };
  for (const k in vars) vars[k] = resolve(vars[k]);
  // 3) un solo blocco per (media, selettore)
  const map = new Map(); const tmp = document.createElement('div');
  const mapSel = s => s.replace(/^(html\s+)?body(?=[\s.:#\[>~+]|$)/, '.pp-root').replace(/#product-page-v8/g, '.pp-root');
  for (const [media, selText, css] of rules) {
    const clean = resolve(css).split(';').filter(d => d.trim() && !d.trim().startsWith('--')).join(';');
    if (!clean.trim()) continue;
    for (let sel of splitSel(selText)) {
      if (/^(:root|::backdrop)$/.test(sel)) continue;
      sel = mapSel(sel);
      const key = media + '|' + sel; const prev = map.get(key);
      tmp.style.cssText = prev ? prev.css : '';
      const s2 = document.createElement('div').style; s2.cssText = clean;
      for (let i = 0; i < s2.length; i++) { const p = s2[i];
        if (tmp.style.getPropertyPriority(p) === 'important' && s2.getPropertyPriority(p) !== 'important') continue;
        tmp.style.setProperty(p, s2.getPropertyValue(p), s2.getPropertyPriority(p)); }
      if (prev) map.delete(key);
      map.set(key, { media, sel, css: tmp.style.cssText });
    }
  }
  // 4) serializza: blocchi consecutivi con stesso media nello stesso @media
  let out = keep.filter(t => t.startsWith('@keyframes')).join('\n') + '\n'; let cur = null;
  for (const { media, sel, css } of map.values()) {
    if (media !== cur) { if (cur) out += '}'; if (media) out += '@media ' + media + '{'; cur = media || null; }
    out += sel + '{' + css + '}';
  }
  if (cur) out += '}';
  // wrapper
  const w = document.createElement('div'); w.className = 'pp-root';
  while (document.body.firstChild) w.appendChild(document.body.firstChild);
  document.body.appendChild(w); document.body.removeAttribute('id');
  return { css: out, body: document.body.innerHTML, nvars: Object.keys(vars).length, nrules: map.size };
}'''


async def run(lang):
    src = f'{ROOT}/{lang}/index.html'
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        await pg.goto('file://' + src)
        res = await pg.evaluate(JS)
        await b.close()
    html = open(src).read()
    import re
    head = re.search(r'<head>(.*?)<style>', html, re.S).group(1)
    head = re.sub(r'<link[^>]*fonts\.(googleapis|gstatic)[^>]*>', '', head)
    faces = ''.join("@font-face{font-family:'%s';font-weight:%d;font-style:normal;font-display:swap;src:url(%s%s.woff2) format('woff2')}" % (f, w, FONTS, n) for f, w, n in FACES)
    css = faces + res['css']
    css = re.sub(r'\s*!important', '!important', css)
    out = f'<!DOCTYPE html>\n<html lang="{"de" if lang == "de" else "en-GB"}"><head>{head}<style>{css}</style></head><body>{res["body"]}</body></html>'
    open(src, 'w').write(out)
    print(lang, 'vars', res['nvars'], 'rules', res['nrules'], 'size', len(out), 'css', len(css))


for l in sys.argv[1:] or ['uk', 'de']:
    asyncio.run(run(l))
