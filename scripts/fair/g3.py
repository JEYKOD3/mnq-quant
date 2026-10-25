import json, itertools
out=[]
# neighbourhood of the news-only survivor
for tf, sig, t0, (S,Tg,m) in itertools.product([1,2,3,5],['two','either','disp','bos','aplus'],[570,585,600,615],
        [(38,38,'fixed'),(50,50,'fixed'),(63,63,'fixed'),(50,76,'fixed'),(38,57,'fixed'),(50,0,'fair')]):
    out.append(dict(fair='news_only',news='only',tf=tf,sig=sig,t0=t0,stop=S,tgt=Tg or 38,tgt_mode=m))
# stop sized to the daily range, fixed 1:1 and 1:1.5
for fair, tf, sig, k, rr in itertools.product(['open','news'],[1,2],['either','aplus','two'],[.1,.15,.2],[1,1.5]):
    out.append(dict(fair=fair,tf=tf,sig=sig,t0=585,stop=25,tgt=25*rr,stop_mode='adr',adrk=k))
open('g3.jsonl','w').write('\n'.join(json.dumps(c) for c in out)+'\n'); print(len(out))
