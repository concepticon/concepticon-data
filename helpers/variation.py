# author   : Johann-Mattis List
# email    : mattis.list@uni-marburg.de
# created  : 2015-06-19 10:07
# modified : 2015-06-19 10:07
"""
Compute the variation for concept glosses in the concepticon data.
"""

__author__="Johann-Mattis List"
__date__="2015-06-19"

from concepticondata.util import *
from glob import glob

lists = glob('../concepticondata/conceptlists/*.tsv')

D = {}
for l in lists:
    
    name = l.split('/')[-1].strip('.tsv')
    print("Loading {0}...".format(name))
    d = load_conceptlist(l)
    for a in [x for x in d if '-' in x]:
        tmp = d[a] 
        gloss = tmp['GLOSS'] if 'GLOSS' in tmp else tmp['ENGLISH']
        clab = tmp['CONCEPTICON_GLOSS']
        try:
            D[clab] += [(gloss,name)]
        except KeyError:
            D[clab] = [(gloss,name)]

for k,v in sorted(
        D.items(), 
        key=lambda x: len(set([y[0] for y in x[1]]))
        ):
    print(k, '\t', len(set([x[0] for x in v])))

