import json,re,sys,glob,os
# usage: extract.py <toolu json> <videoid>
d=json.load(open(sys.argv[1]))
vid=sys.argv[2]
parts=[]; title=''
for x in d:
    if x['type']!='text': continue
    t=x['text']
    if t.startswith('[get_page_text]'):
        m=re.search(r'---\n([^\n]*)\n\n(.*)',t,re.S)
        if not m: continue
        title=m.group(1); body=m.group(2)
        if body.startswith('pad pad'): continue
        parts.append(body.strip())
body=' '.join(parts)
open(f'tx/{vid}.txt','w').write(title+'\n\n'+body)
print(vid,title,len(body))
