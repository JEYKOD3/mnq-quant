import sys, json, itertools, multiprocessing as mp
from fp import run, stats
def one(cfg):
    try: s = stats(run(**cfg))
    except Exception as e: s = dict(err=str(e))
    return dict(cfg=cfg, **s)
if __name__ == '__main__':
    cfgs = [json.loads(l) for l in open(sys.argv[1])]
    with mp.Pool(2) as p, open(sys.argv[2], 'w') as f:
        for i, r in enumerate(p.imap_unordered(one, cfgs, chunksize=4)):
            f.write(json.dumps(r) + '\n'); f.flush()
