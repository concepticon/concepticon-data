# author   : Johann-Mattis List
# email    : mattis.list@uni-marburg.de
# created  : 2015-08-21 18:56
# modified : 2015-08-21 18:56
"""
Adjust a previously mapped wordlist by adding new glosses to the concepticon. 
"""

__author__="Johann-Mattis List"
__date__="2015-08-21"

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
for line in data:
    tmp = dict(zip(lhead, line))

    outl = []
    #outl += [argv[1].split('/')[-1].replace('.map.tsv','')]
    new_id = False
    gloss = ''
    for h in lhead:
        if h == 'CONCEPTICON_ID':
            if int(tmp[h]) == 0:
                outl += [str(next_id)]
                next_id += 1
                new_id = True
            else:
                outl += [str(tmp[h])]
                gloss = i2c[int(tmp[h])]
        else:
            if new_id and h == 'CONCEPTICON_GLOSS':
                outl += [tmp[h].split(':')[0]]
            elif h == 'CONCEPTICON_GLOSS':
                outl += [gloss]
                
                # split stuff
                new_items += [[str(next_id -1), tmp[h].split(':')[0], tmp[h]]]
            elif h != 'MATCH':
                outl += [tmp[h]]
    cleaned_list += [outl]

name = argv[1].split('/')[-1].replace('.mapped.tsv', '-')
for line in sorted(cleaned_list, key=lambda x: (int(''.join([y for y in x[0] if
    y.isdigit()])),x[0])):
    print(name+line[0]+'\t'+'\t'.join(line))

