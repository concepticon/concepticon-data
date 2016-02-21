from lingpy import *
from concepticondata import *
from concepticondata.util import *
from sys import argv

cpath = '../concepticondata/concepticon.tsv'
bpath = cpath 
baselist = csv2list(bpath)


header = baselist[0]
ids = [int(line[0]) for line in baselist[1:]]
concepts = [line[1] for line in baselist[1:]]


c2i = dict(zip(concepts, ids))
i2c = dict(zip(ids, concepts))

# load the new list
newlist = csv2list(argv[1])

lhead = newlist[0]
data = newlist[1:]
idx = 1
new_items = []
cleaned_list = [] #["ID"] + lhead]
next_id = max(ids)+1
wiki = []
new_lines = []
for line in data:
    print('Processing:', line[0], line[1])
    tmp = dict(zip(lhead, line))
    outl = []
    #outl += [argv[1].split('/')[-1].replace('.map.tsv','')]
    new_id = False

    cid = tmp['CONCEPTICON_ID']
    cig = tmp['CONCEPTICON_GLOSS']

    if cig.startswith('>>'):
        cid = str(next_id)
        next_id += 1
        gloss, definition = cig[2:].split(':')
        if gloss.endswith('!w'):
            gloss = gloss[:-2]
            wiki += [(cid, gloss)]
        gloss = gloss.upper()
        if gloss in concepts:
            raise ValueError("Gloss {0} is in the list.".format(gloss))

        new_items += [(cid, gloss, definition)]
        tmp['CONCEPTICON_ID'] = cid
        tmp['CONCEPTICON_GLOSS'] = gloss
    new_lines += [[tmp[h] for h in lhead]]

name = argv[1].split('/')[-1].replace('.mapped.tsv', '-')
#for line in sorted(cleaned_list, key=lambda x: (int(''.join([y for y in x[0] if
#    y.isdigit()])),x[0])):
#    print(name+line[0]+'\t'+'\t'.join(line))

for line in new_items:
    print('\t'.join(line))

with open(argv[1], 'w') as f:
    f.write('\t'.join(lhead)+'\n')
    for line in new_lines:
        f.write('\t'.join(line)+'\n')
