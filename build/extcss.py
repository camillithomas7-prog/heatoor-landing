"""Sposta il CSS in un file esterno: l'importer CC lo tiene così com'è (non passa dall'editor)."""
import re, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://camillithomas7-prog.github.io/heatoor-landing/'
for lang in sys.argv[1:] or ['uk', 'de']:
    p = f'{ROOT}/{lang}/index.html'; h = open(p).read()
    m = re.search(r'<style>(.*)</style>', h, re.S)
    if not m: continue
    # nome file diverso a ogni versione: CC tiene il primo file importato con lo stesso nome
    import hashlib, glob; v = hashlib.md5(m.group(1).encode()).hexdigest()[:8]
    for old in glob.glob(f'{ROOT}/{lang}/style*.css'): os.remove(old)
    open(f'{ROOT}/{lang}/style-{v}.css', 'w').write(m.group(1))
    h = h.replace(m.group(0), f'<link rel="stylesheet" href="{BASE}{lang}/style-{v}.css">')
    open(p, 'w').write(h)
    print(lang, 'html', len(h), 'css', len(m.group(1)))
