import re,json,sys,os
from bs4 import BeautifulSoup, Comment
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE='https://camillithomas7-prog.github.io/heatoor-landing/assets/'
CHECKOUT='/checkout'
POLICY={'terms-conditions':'/terms-of-service','privacy-policy':'/privacy-policy','cookie-policy':'/privacy-policy',
        'returns-cancellation':'/refund-policy','shipping-delivery':'/shipping-policy','contact-us':'/contact-us','affiliate':'/contact-us'}
src=open(f'{ROOT}/src/index.html').read()
strings=json.load(open(f'{ROOT}/build/strings.json'))

def build(lang):
    copy=json.load(open(f'{ROOT}/build/copy_{lang}.json'))
    tr=dict(zip(strings,copy))
    s=BeautifulSoup(src,'html.parser')
    css='\n'.join(t.string or '' for t in s.find_all('style'))
    body=s.body
    for t in body.find_all(['script','noscript','style','iframe']): t.decompose()
    for c in body.find_all(string=lambda x:isinstance(x,Comment)): c.extract()
    fi=body.find('section',id='featured-in')
    if fi: fi.decompose()
    for n in list(body.find_all(string=True)):
        t=n.strip()
        if t in tr:
            n.replace_with(n.replace(t,tr[t]) if tr[t] else '')
    for a in body.find_all('a'):
        h=a.get('href','')
        if 'dealshopa' in h or 'checkout' in h: a['href']=CHECKOUT
        elif 'email-protection' in h or 'trackingmore' in h: a['href']='/contact-us'
        elif h.startswith('tel:'): a.parent.decompose() if a.parent and a.parent.name=='li' else a.decompose()
        elif '/legal/' in h:
            k=h.rstrip('/').split('/')[-1]; a['href']=POLICY.get(k,'/contact-us')
    for src_ in body.find_all('source'):
        if src_.get('data-src'): src_['src']=src_['data-src']; del src_['data-src']
    for v in body.find_all('video'):
        if v.get('poster'): del v['poster']
    # FAQ senza script (solo onclick, niente '<')
    for c in body.select('#faq_container .questions__card'):
        c['onclick']=("var c=this,o=c.getAttribute('expanded')=='true';"
          "[].forEach.call(document.querySelectorAll('#faq_container .questions__card'),function(x){x.setAttribute('expanded','false');x.classList.add('questions__card-hover');x.querySelector('.questions__listWrap').style.height='0px'});"
          "if(!o){c.setAttribute('expanded','true');c.classList.remove('questions__card-hover');var w=c.querySelector('.questions__listWrap');w.style.height=w.firstElementChild.offsetHeight+'px'}")
        c['style']='cursor:pointer'
    btn=body.find(id='header__menuBtn')
    if btn:
        btn['onclick']=("var m=document.querySelector('.navigation--mobile'),o=this.getAttribute('aria-expanded')=='true';"
          "this.setAttribute('aria-expanded',o?'false':'true');this.classList.toggle('is-active',!o);m.setAttribute('aria-expanded',o?'false':'true');"
          "m.classList.remove('navigation__opacity');m.classList.toggle('navigation--mobile-enabled',!o);m.classList.toggle('navigation--mobile-disabled',o);m.style.height=o?'0':(m.scrollHeight+1)+'px'")
    for a in body.select('.navigation-link--mobile'):
        a['onclick']="document.getElementById('header__menuBtn').click()"
    fl=body.find('section',class_='floater')
    if fl: fl['class']=fl.get('class',[])+['is-visible']
    html=str(body)
    html=re.sub(r'https://(?:get-heatoor\.com|cdn\.get-heatoor\.com)/[^"\'\s)]*?/?([^/"\'\s)?]+\.(?:jpg|jpeg|png|svg|webp|mp4|gif))',
                lambda m: BASE+(('ui-' if any(k in m.group(0) for k in ('fallbacks','/stars/','/icons/')) and not os.path.exists(f'{ROOT}/assets/{m.group(1)}') or os.path.exists(f'{ROOT}/assets/ui-{m.group(1)}') and any(k in m.group(0) for k in ('fallbacks','/stars/','/icons/')) else '')+m.group(1)),html)
    css=re.sub(r'https://(?:get-heatoor\.com|cdn\.get-heatoor\.com)/[^"\'\s)]*?/?([^/"\'\s)?]+\.(?:jpg|jpeg|png|svg|webp|gif))',lambda m: BASE+m.group(1),css)
    html=re.sub(r'\s+srcset="[^"]*"','',html)
    html=re.sub(r'\n\s*\n+','\n',html)
    html=re.sub(r'[ \t]{2,}',' ',html)
    title={'uk':'Heatoor – Plug-In Heater | Up to 75% Off','de':'Heatoor – Heizgerät für die Steckdose | Bis zu 75 % Rabatt'}[lang]
    hl={'uk':'en-GB','de':'de'}[lang]
    os.makedirs(f'{ROOT}/build/tmp',exist_ok=True)
    open(f'{ROOT}/build/tmp/{lang}.css','w').write(css)
    open(f'{ROOT}/build/tmp/{lang}.body','w').write(html)
    open(f'{ROOT}/build/tmp/{lang}.meta','w').write(json.dumps({'title':title,'lang':hl}))
for l in ('uk','de'): build(l)
