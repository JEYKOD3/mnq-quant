import pandas as pd, numpy as np, datetime as dt
from mnqbt import *
from sweep import stats
def load_db(root):
    d=pd.read_csv(f'../data/raw/{root}_5m_cont.csv.gz')
    return list(d.itertuples(index=False,name=None))
B=dict(minBodyFr=0.3,skipLondon=False,hlMode='Structure',useVwapF=False,sigFrac=0.5,useHL=False,useDT=False,blockHours=(6,),htfMin=15,htfMode='price',maxAtrRatio=1.5)
