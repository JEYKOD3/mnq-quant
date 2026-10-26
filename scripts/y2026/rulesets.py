"""Rule sets for the 2026 study. OLD = live Pine v6. NEW = recommended (nothing open after 15:00, D2 out 13:15)."""
from common import *
def OLD(): return old_team()
def NEW(): return sorted(news() + v4(flat=900) + d2(th=.6, flat=795) + tdp(tgtR=1.5, flat=900) + pinball(tgtR=2, cap=180, flat=900) + h2(tgtR=2, flat=900), key=lambda t: (t['d'], t['eT']))
def NEW14(): return sorted(news() + v4(flat=900) + d2(th=.6, flat=795) + tdp(tgtR=1.5, flat=840) + pinball(tgtR=2, cap=180, flat=840) + h2(tgtR=2, flat=840), key=lambda t: (t['d'], t['eT']))
def NEWP(): return sorted(news() + v4(flat=900) + d2(th=.6, flat=795) + tdp(tgtR=1.5, flat=900) + pinball(tgtR=None, cap=180, flat=900) + h2(tgtR=2, flat=900), key=lambda t: (t['d'], t['eT']))
SETS = {'OLD': OLD, 'NEW': NEW, 'NEW14': NEW14, 'NEWP': NEWP}
