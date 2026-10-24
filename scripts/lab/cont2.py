import sys; sys.path.insert(0,'.')
from cont import *
for ET_ in (630,690,720,780):
    for th in (.4,.6,.8):
        for st in ('open','lod','pdc'):
            rep(f"refPDC T={ET_//60}:{ET_%60:02d} th{th} stop {st}",cont(ET_,th,ref='pdc',stop=st))
print('### D2 (ref open) refinements')
for ET_ in (630,660,690):
    for th in (.4,.5,.6):
        for st in ('open','lod'):
            for fl in (900,955):
                rep(f"D2 T={ET_//60}:{ET_%60:02d} th{th} stop {st} flat {fl}",cont(ET_,th,stop=st,flat=fl))
