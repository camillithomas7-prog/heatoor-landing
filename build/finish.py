import re,json,os
R=os.path.dirname(os.path.abspath(__file__))
for l in ('uk','de'):
    c=open(f'{R}/tmp/out_{l}/{l}.css').read()
    c=re.sub(r'@font-face\s*{[^}]*}','',c)
    c=re.sub(r'/\*.*?\*/','',c,flags=re.S)
    c=re.sub(r'--wp--[\w-]+:[^;}]*;?','',c)
    c=re.sub(r'[^{}]*{\s*}','',c)          # regole vuote
    c=re.sub(r'\s+',' ',c); c=re.sub(r'\s*([{};:,>])\s*',r'\1',c); c=c.replace(';}','}')
    m=json.load(open(f'{R}/tmp/{l}.meta')); b=open(f'{R}/tmp/{l}.body').read()
    b=re.sub(r'^<body[^>]*>|</body>$','',b.strip())
    b=re.sub(r'\s+decoding="async"','',b); b=re.sub(r'>\s+<','><',b); b=re.sub(r'\s+',' ',b)
    page=f'''<!DOCTYPE html>
<html lang="{m['lang']}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{m['title']}</title>
<link rel="icon" href="https://camillithomas7-prog.github.io/heatoor-landing/assets/Heatoor_favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Roboto:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>{c}</style></head>
<body id="product-page-v8">{b}</body></html>'''
    os.makedirs(f'{R}/../{l}',exist_ok=True)
    open(f'{R}/../{l}/index.html','w').write(page)
    print(l,len(page),'css',len(c),'lt-in-attr',len(re.findall(r'="[^"]*<[^"]*"',b)))
