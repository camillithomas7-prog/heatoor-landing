"""Ultimo passaggio dopo flatten.py: rende il markup neutro per l'importer CheckoutChamp.

- hero: il gradiente passa su un div .hero__shade, la sezione tiene solo l'immagine (1 layer)
- icona fulmine SVG -> PNG
- id: restano solo le ancore del menu (una volta sola)
- tutte le classi rinominate in codici brevi (nessuna parola tipo "container")
- onclick rigenerati con i nuovi nomi, senza id
"""
import re, sys, os
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANCHORS = {'zigzag', 'setup', 'reviews', 'faq'}


def split_top(v, sep=','):
    out, d, cur = [], 0, ''
    for ch in v:
        if ch == '(': d += 1
        if ch == ')': d -= 1
        if ch == sep and d == 0: out.append(cur.strip()); cur = ''
        else: cur += ch
    if cur.strip(): out.append(cur.strip())
    return out


def decls(body):
    res = []
    for d in split_top(body, ';'):
        if ':' in d:
            k, v = d.split(':', 1); res.append([k.strip(), v.strip()])
    return res


def hero_shade(css):
    """.hero{background-image:grad,url;...} -> .hero{url} + .hero__shade{grad}"""
    def fix(m):
        sel, body = m.group(1), m.group(2)
        if sel != '.hero': return m.group(0)
        ds = decls(body); hero, shade = [], []
        for k, v in ds:
            if k in ('background-image', 'background-position', 'background-size', 'background-repeat', 'background-position-x', 'background-position-y'):
                parts = split_top(v)
                if len(parts) == 2:
                    shade.append([k, parts[0]]); hero.append([k, parts[1]]); continue
            hero.append([k, v])
        out = '.hero{' + ';'.join(f'{k}:{v}' for k, v in hero) + '}'
        if shade:
            out += '.hero__shade::before{' + ';'.join(f'{k}:{v}' for k, v in shade) + '}'
        return out
    return re.sub(r'(?<=[{}])(\.hero)\{([^{}]*)\}', fix, css)


def run(lang):
    path = f'{ROOT}/{lang}/index.html'
    html = open(path).read()
    css = re.search(r'<style>(.*)</style>', html, re.S).group(1)
    css = hero_shade('}' + css)[1:]
    # gli sfondi stanno su ::before: CC copia lo sfondo degli elementi in uno style inline (lazy) e batte i @media
    css += ('.hero__shade{position:absolute;top:0;left:0;right:0;bottom:0;pointer-events:none;z-index:0}'
            '.hero__shade::before{content:"";position:absolute;top:0;left:0;right:0;bottom:0;background-repeat:no-repeat}'
            '.hero__container{position:relative;z-index:1}')
    # CC mette la prima immagine di sfondo della sezione come style inline (lazy) e batte i @media:
    # l'immagine hero diventa <img> vere, la sezione resta senza background-image
    hero_imgs = {}
    def strip_bg(m):
        body = m.group(2)
        u = re.search(r'background-image:\s*url\(["\']?([^"\')]+)["\']?\)', body)
        if u: hero_imgs.setdefault(u.group(1), True)
        body = re.sub(r'background-(image|position|size|repeat|position-x|position-y):[^;]*;?', '', body)
        return m.group(1) + '.hero{' + body + '}'
    css = re.sub(r'(^|[{}])\.hero\{([^{}]*)\}()', strip_bg, css)
    urls = list(hero_imgs)
    desk = [u for u in urls if 'ZGVza3RvcF' in u and 'h_900' in u][0]
    mob = [u for u in urls if 'bW9iaWxl' in u][0]
    css += ('.hero__img{position:absolute;left:0;z-index:0;pointer-events:none;display:block;max-width:none}'
            '.hero__img--d{top:0;width:100%;height:100%;object-fit:cover;object-position:100% 50%}'
            '.hero__img--m{display:none}'
            '@media screen and (max-width:992px) and (min-width:769px){.hero__img--d{top:194px;height:auto}}'
            '@media screen and (max-width:768px){.hero__img--d{display:none}.hero__img--m{display:block;top:140px;width:100%;height:auto}}')
    for bp, y in ((650, 150), (550, 165), (510, 215), (471, 270), (460, 132), (340, 152)):
        css += f'@media screen and (max-width:{bp}px){{.hero__img--m{{top:{y}px}}}}'
    s = BeautifulSoup(html, 'html.parser')
    hero = s.select_one('section.hero')
    shade = s.new_tag('div', attrs={'class': 'hero__shade'}); hero.insert(0, shade)
    hero.insert(0, s.new_tag('img', attrs={'class': 'hero__img hero__img--m', 'src': mob, 'alt': ''}))
    hero.insert(0, s.new_tag('img', attrs={'class': 'hero__img hero__img--d', 'src': desk, 'alt': ''}))
    # icone piccole -> span con sfondo CSS (l'importer CC a volte mette il segnaposto sulle <img>)
    ICONS = {'ui-thunder-icon.svg': ('ico-thunder', 'thunder-2.png', 20, 20), 'ui-footer_arrow.svg': ('ico-arrow', 'ui-footer_arrow.svg', 14, 8)}
    used = {}
    for img in s.find_all('img'):
        for key, (cls, fn, w, h) in ICONS.items():
            if img.get('src', '').endswith(key):
                sp = s.new_tag('span', attrs={'class': img.get('class', []) + [cls]})
                img.replace_with(sp); used[cls] = (img['src'].rsplit('/', 1)[0] + '/' + fn, w, h)
    for cls, (url, w, h) in used.items():
        css += (f'.{cls}{{display:inline-block;flex:none;width:{w}px;height:{h}px}}'
                f'.{cls}::before{{content:"";display:block;width:100%;height:100%;background:url("{url}") center/contain no-repeat}}')
    btn0 = s.select_one('.header__menuBtn')
    lines = btn0.select('svg path') if btn0 else []
    for el in lines:
        if el.get('id') in ('top-line', 'middle-line', 'bottom-line'): el['class'] = el.get('class', []) + [el['id']]
    # id: solo ancore, prima occorrenza
    seen = set()
    for el in s.find_all(id=True):
        i = el['id']
        if i in ANCHORS and i not in seen: seen.add(i); continue
        del el['id']
    # svg del menu: #top-line ecc. -> classi
    css = re.sub(r'#(top-line|middle-line|bottom-line)', r'.\1', css)
    # rinomina classi
    names = []
    for el in s.find_all(class_=True):
        for c in el['class']:
            if c not in names: names.append(c)
    extra = ['is-visible', 'is-active', 'navigation--mobile-enabled', 'navigation--mobile-disabled',
             'navigation__opacity', 'questions__card-hover', 'questions__svg-active']
    for c in extra + re.findall(r'\.(-?[_a-zA-Z][\w-]*)', css):
        if c not in names: names.append(c)
    def code(n):
        a = 'abcdefghijklmnopqrstuvwxyz'; s_ = ''
        n += 26
        while n: s_ = a[n % 26] + s_; n //= 26
        return 'h' + s_
    cmap = {c: code(i) for i, c in enumerate(names)}
    for el in s.find_all(class_=True):
        el['class'] = [cmap[c] for c in el['class']]
    # CSS: rinomina solo nei selettori
    def ren_sel(sel):
        return re.sub(r'\.(-?[_a-zA-Z][\w-]*)', lambda m: '.' + cmap.get(m.group(1), m.group(1)), sel)
    css = re.sub(r'(^|[{}])([^{}@]+)\{', lambda m: m.group(1) + ren_sel(m.group(2)) + '{', css)
    C = lambda c: cmap[c]
    # onclick
    for el in s.find_all(onclick=True): del el['onclick']
    faq_cards = s.select('.' + C('questions__card'))
    for c in faq_cards:
        c['onclick'] = (f"var c=this,o=c.getAttribute('expanded')=='true';"
                        f"[].forEach.call(document.querySelectorAll('.{C('questions__card')}'),function(x){{x.setAttribute('expanded','false');x.classList.add('{C('questions__card-hover')}');x.querySelector('.{C('questions__listWrap')}').style.height='0px'}});"
                        f"if(!o){{c.setAttribute('expanded','true');c.classList.remove('{C('questions__card-hover')}');var w=c.querySelector('.{C('questions__listWrap')}');w.style.height=w.firstElementChild.offsetHeight+'px'}}")
    b = s.select_one('.' + C('header__menuBtn'))
    if b:
        b['onclick'] = (f"var m=document.querySelector('.{C('navigation--mobile')}'),o=this.getAttribute('aria-expanded')=='true';"
                        f"this.setAttribute('aria-expanded',o?'false':'true');this.classList.toggle('{C('is-active')}',!o);m.setAttribute('aria-expanded',o?'false':'true');"
                        f"m.classList.remove('{C('navigation__opacity')}');m.classList.toggle('{C('navigation--mobile-enabled')}',!o);m.classList.toggle('{C('navigation--mobile-disabled')}',o);m.style.height=o?'0':(m.scrollHeight+1)+'px'")
    for a in s.select('.' + C('navigation-link--mobile')):
        a['onclick'] = f"document.querySelector('.{C('header__menuBtn')}').click()"
    for h in s.select('.' + C('footer__heading')):
        h['onclick'] = ("if(window.innerWidth>767)return;var l=this.parentNode,u=l.querySelector('ul'),c=l.querySelector('." + C('footer__chevron') + "'),o=u.getAttribute('expanded')=='true';"
                        "u.setAttribute('expanded',o?'false':'true');u.style.height=o?'0px':u.scrollHeight+'px';u.style.marginBottom=o?'0px':'25px';u.style.marginTop=o?'0px':'-9px';if(c)c.style.transform=o?'rotate(-90deg)':'rotate(0deg)'")
    out = str(s)
    out = re.sub(r'<style>.*</style>', lambda m: '<style>' + css + '</style>', out, flags=re.S)
    open(path, 'w').write(out)
    print(lang, 'classi', len(cmap), 'size', len(out), 'lt-in-attr', len(re.findall(r'="[^"]*<[^"]*"', str(s.body))))


for l in sys.argv[1:] or ['uk', 'de']:
    run(l)
