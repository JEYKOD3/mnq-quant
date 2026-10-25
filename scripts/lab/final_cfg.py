"""Final defaults 2026-10-25: V4+ 1.25R target + breakeven at +1R, D2 as is, Pinball hold to 15:55, H2 0.40 threshold 2R, shared daily risk budget."""
import sys; sys.path.insert(0,'.')
exec(open('rr125.py').read().split('TR={k:build')[0].split('VAR={')[0])
VAR={"Before (Oct 24 rules)":(dict(),"current"),"New defaults":(dict(be=True,v4t=1.25),"updated"),"New defaults, no breakeven":(dict(v4t=1.25),"updated")}
exec('TR={k:build'+open('rr125.py').read().split('TR={k:build')[1].replace("k.startswith(('A','C'))","True"))
