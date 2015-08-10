# author   : Johann-Mattis List
# email    : mattis.list@uni-marburg.de
# created  : 2015-06-11 09:09
# modified : 2015-06-11 09:09
"""
Compare two conceptlists.
"""

__author__="Johann-Mattis List"
__date__="2015-06-11"

from sys import argv
from lingpyd import *
from concepticondata.util import load_conceptlist

def simple_comparison(list1,list2):
    
    clist1 = load_conceptlist(
            '../concepticondata/conceptlists/'+list1+'.tsv'
            )
    clist2 = load_conceptlist(
            '../concepticondata/conceptlists/'+list2+'.tsv'
            )

    gidx1 = 'ENGLISH' if 'ENGLISH' in clist1['header'] else 'GLOSS'
    gidx2 = 'ENGLISH' if 'ENGLISH' in clist2['header'] else 'GLOSS'

    clist2_keys = []
    for k in clist2:
        if k not in ['header','splits','mergers']:
            clist2_keys += [(clist2[k]['CONCEPTICON_ID'], k)]
    clist2_keys = dict(clist2_keys)

    coverage = []
    count = 0
    for k in clist1:
        if k not in ['header', 'splits', 'mergers']:
            cid = clist1[k]['CONCEPTICON_ID']
            if cid in clist2_keys:
                coverage += [(cid, k, clist1[k][gidx1],
                    clist2_keys[cid], clist2[clist2_keys[cid]][gidx2])]
                count += 1
            else:
                coverage += [(cid, k, clist1[k][gidx1],'?','?')]
    
    for line in coverage:
        print('\t'.join(line))
    print(count / len(clist1), count)
    


