from concepticondata.util import *
from lingpy import *
import lingpy
from glob import glob
from sys import argv
import networkx as nx
from sys import argv

clists = glob('../concepticondata/conceptlists/*.tsv')
concepticon = dict([(a,b) for a,*b in csv2list('../concepticondata/concepticon.tsv',
    strip_lines=False)])

#clists = [l for l in clists if len(l.split('-')[-1][:-4]) == 3 and
#        l.split('-')[-1][0] in '12']
print(len(clists))


G = nx.Graph()
C = {}

if 'best' in argv:
    for i,l1 in enumerate(clists):
        
        list1 = load_conceptlist(l1)
        name1 = l1.split('/')[-1][:-4]
        if 'GLOSS' in list1['header']:
            key = 'GLOSS'
        else:
            key = 'ENGLISH'
    
        set1 = dict(set([
                (list1[k]['CONCEPTICON_ID'], list1[k][key]) for k in list1 if k not in 
                ['header','splits','mergers']
                ]))
        print('[i] analyzing list {0}...'.format(name1))
        for k in set1:
            try:
                C[k] += [name1]
            except KeyError:
                C[k] = [name1]
    
    print(len([x for x in C if len(C[x]) >= 70]))
    
    best_concepts = []
    with open('best-concepts.tsv', 'w') as f:
        for x in C:
            if len(C[x]) >= 50:
                f.write(x+'\n')
                best_concepts += [x]
    print(len(best_concepts))


else:

    best_concepts = [x[0] for x in csv2list('best-concepts.tsv')]


_clists = []
STATES = {}
for i,l1 in enumerate(clists):
    
    list1 = load_conceptlist(l1)
    name1 = l1.split('/')[-1][:-4]
    if 'GLOSS' in list1['header']:
        key = 'GLOSS'
    else:
        key = 'ENGLISH'

    set1 = dict(set([
            (list1[k]['CONCEPTICON_ID'], list1[k][key]) for k in list1 if k not in 
            ['header','splits','mergers']
            ]))
    
    if len([k for k in set1 if k in best_concepts]) >= 70:
        if 'GLOSS' in list1['header']:
            pass
        else:
            _clists += [l1]

            for k in best_concepts:
                
                try:
                    v = set1[k]
                except:
                    v = '?'

                try:
                    STATES[k] += [v]
                except KeyError:
                    STATES[k] = [v]

for k,v in STATES.items():
    states = sorted(set(v))
    tmp = {}
    for i,j in zip(states,'abcdefghijklmnopqrstuvw'):
        if i != '?':
            tmp[i] = j
        else:
            tmp[i] = '?'
    STATES[k] = tmp
input('bishier')






print(len(_clists))

M = [[0 for l in _clists] for n in _clists]
names = []

states = ''

for i,l1 in enumerate(_clists):
    
    list1 = load_conceptlist(l1)
    name1 = l1.split('/')[-1][:-4]
    names += [name1.replace('-','_')]
    if 'GLOSS' in list1['header']:
        key = 'GLOSS'
    else:
        key = 'ENGLISH'

    set1 = dict(set([
            (list1[k]['CONCEPTICON_ID'], list1[k][key]) for k in list1 if k not in 
            ['header','splits','mergers']
            ]))
    print('[i] analyzing list {0}...'.format(name1))

    states += name1+'\t'
    for k in best_concepts:
        if k in set1:
            states += STATES[k][set1[k]]
        else:
            states += '?'
    states += '\n'

    for j,l2 in enumerate(_clists):
        if i < j:

            list2 = load_conceptlist(l2)
            name2 = l2.split('/')[-1][:-4]

            if 'GLOSS' in list2['header']:
                key = 'GLOSS'
            else:
                key = 'ENGLISH'
            
            set2 = dict(set([
                (list2[k]['CONCEPTICON_ID'], list2[k][key]) for k in list2 if k not in 
                ['header','splits','mergers']
                ]))

            commons = [k for k in set1 if k in set2]
            ld = []
            for k in best_concepts:
                if k in set1 and k in set2:
                    if set1[k] == set2[k]:
                        ld += [0]
                    else:
                        ld += [0.95]
                else:
                    pass
                    #ld += [1]

                #ld += [edit_dist(set1[k],set2[k], normalized=True)]
            if ld:
                d = sum(ld) / len(ld)
            else:
                d = 1

            if d < 0.05:
                G.add_edge(name1, name2, weight=1-d)
            M[i][j] = d
            M[j][i] = d
                

with open('states.nex', 'w') as f:
    f.write(states)


txt = lingpy.convert.strings.matrix2dst(M, taxa=names, taxlen=0)
with open('distances.dst', 'w') as f:
    f.write(txt)

nx.write_gml(G, 'network.gml')
