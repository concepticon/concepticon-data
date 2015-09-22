from lingpy import *

# get the concepticon
cp = csv2list('../concepticondata/concepticon.tsv', strip_lines=False)
C = dict(
        [(line[2], line[0]) for line in cp[1:]]
        )

# get the list
from sys import argv
csv = csv2list(argv[1], strip_lines=False)

# get idx of concepticon gloss and concepticon id
gidx = csv[0].index('CONCEPTICON_GLOSS')
idx = csv[0].index("CONCEPTICON_ID")

# iterate and check
for i,line in enumerate(csv[1:]):
    if len(line) != len(csv[0]):
        pass
    else:
        if line[gidx].startswith('!'):
            csv[i+1][idx] = C[line[gidx][1:]]
            csv[i+1][gidx] = line[gidx][1:]
with open(argv[1], 'w') as f:
    for line in csv:
        f.write('\t'.join(line)+'\n')
        
