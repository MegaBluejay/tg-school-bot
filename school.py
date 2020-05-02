from datetime import time,datetime
from bisect import bisect
from ruamel.yaml import YAML
from pathlib import Path
yaml = YAML(typ='safe')

sched = [(9, 15), (10, 0), (10, 10), (10, 55), (11, 10), (11, 55), (12, 10), (12, 55), (13, 25), (14, 10), (14, 20),
             (15, 5)]
rasp = yaml.load(Path('./rasp'))

def digest(t):
    breaks = [datetime.combine(t.date(), time(*tm)) for tm in sched]
    dotw = t.strftime('%a')
    pos = bisect(breaks,t)
    if pos==len(breaks) or dotw=='Sun':
        return None,None,None,'none','none'
    is_lesson = pos%2
    n = pos//2 + pos%2
    left = breaks[pos]-t

    if n:
        current = rasp[dotw][n-1]
    else:
        current = 'none'
    if n<len(rasp[dotw]):
        nxt = rasp[dotw][n]
    else:
        nxt = 'none'
    return is_lesson,n,left,current,nxt
