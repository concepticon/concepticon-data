"""
Script corrects the labels in the network and reduces all relations to one
relation per concept pair as a minimum
"""

from lingpy import *

D = csv2list('../concepticondata/conceptrelations.tsv', strip_lines=False)
_C = csv2list('../concepticondata/concepticon.tsv', strip_lines=False)
C = dict([(a,b) for a,*b in _C[1:]])

with open('../concepticondata/conceptrelations.modified.tsv', 'w') as f:

    f.write('SOURCE\tSOURCE_GLOSS\tRELATION\tTARGET\tTARGET_GLOSS\n')
    visited = []
    for line in D[1:]:
        if len(line) == 3:
            s,r,t = line
        else:
            s,_s,r,t,_t = line

        sg = C[s][1]
        tg = C[t][1]
        if set([s,t]) not in visited:
            visited += [set([s,t])]

            f.write('{0}\t{1}\t{2}\t{3}\t{4}\n'.format(
                s,sg,r,t,tg))
