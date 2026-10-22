import re,sys
f=sys.argv[1]
t=open(f).read()
lines=t.split('\n',2)
body=lines[2]
plain=body
key=' '.join(re.sub(r'\[\d+:\d+\] ','',body[:300]).split()[:15])
i=plain.find(key,50)
print('=====',f,lines[0],'| repeat at',i,'of',len(body))
print(body[:i] if i>0 else body)
