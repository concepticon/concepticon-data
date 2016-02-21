"""
Reduce a list to its unique labels.
"""
from lingpy import *
from sys import argv

csv = csv2list(argv[1])
header = [x.lower() for x in csv[0]]
head = argv[2].lower()
rest = [h for h in header if h != head]

D = {}
for line in csv[1:]:
    
    tmp = dict(zip(header,line))
    
    try:
        for h in rest:
            D[tmp[head]][h] += [tmp[h]]
    except KeyError:
        D[tmp[head]] = {}
        for h in rest:
            D[tmp[head]][h] = [tmp[h]]

with open(argv[1].replace('.tsv','.shrink.tsv'), 'w') as f:
    
    f.write('\t'.join([x.upper() for x in [head]+rest])+'\n')
    for k in sorted(D):

        f.write(k)
        for h in rest:
            f.write('\t'+' / '.join(sorted(set(D[k][h]))))
        f.write('\n')

        

