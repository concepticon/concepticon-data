"""
Script corrects the labels in the network and reduces all relations to one
relation per concept pair as a minimum
"""

from lingpy import *
relations = dict(
    broader = 'narrower',
    resultof = 'resultsin',
    produces = 'producedby',
    usedfor = 'requires',
    classof = 'instanceof',
    intransitiveof = 'transitiveof',
    baseof = 'hasform'
        )
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
            try:
                s,_s,r,t,_t = line
            except ValueError:
                print(line)
                raise ValueError

        sg = C[s][0]
        tg = C[t][0]
        if set([s,t]) not in visited:
            visited += [set([s,t])]
            if r in relations:
                items = [t, tg, relations[r], s, sg]
            else:
                items = [s, sg, r, t, tg]

            f.write('{0}\t{1}\t{2}\t{3}\t{4}\n'.format(
                *items)) #s,sg,r,t,tg))
