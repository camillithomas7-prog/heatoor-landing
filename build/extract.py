import re,json,sys
from bs4 import BeautifulSoup, NavigableString, Comment
h=open('src/index.html').read()
s=BeautifulSoup(h,'html.parser')
body=s.body
for t in body.find_all(['script','noscript']): t.decompose()
seen=[]
for n in body.find_all(string=True):
    if isinstance(n,Comment) or n.parent.name=='style': continue
    t=n.strip()
    if t and t not in seen: seen.append(t)
json.dump(seen,open('build/strings.json','w'),ensure_ascii=False,indent=0)
for i,t in enumerate(seen): print(i,repr(t))
