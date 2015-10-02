# author   : Johann-Mattis List
# email    : mattis.list@uni-marburg.de
# created  : 2015-04-21 09:15
# modified : 2015-04-21 09:15
"""
Refine the data by replacing glosses by the concepticon.tsv glosses.
"""

__author__="Johann-Mattis List"
__date__="2015-04-21"


from concepticondata.util import *
from lingpy import *
from glob import glob
from sys import argv
import networkx as nx

clists = glob('../concepticondata/conceptlists/*.tsv')
concepticon = dict([(a,b) for a,*b in csv2list('../concepticondata/concepticon.tsv',
    strip_lines=False)])

# load concept graph to resolve identity relations
_G = nx.read_gml('../concepticondata/conceptrelations.gml')
G = nx.Graph()
# remove edges which do not have a sameas-relation
for a,b,d in _G.edges(data=True):

    if d['relation'] == 'sameas':
        G.add_edge(_G.node[a]['cid'],_G.node[b]['cid'])
        
# get connected components
ccomps = nx.connected_components(G)

# refine concepticon stuff by taking lowest item of each cluster
converter = {}
for ccomp in ccomps:    
    target = sorted(ccomp, key=lambda x: int(x))[0]
    for c in ccomp:
        converter[str(c)] = str(target)
for k in concepticon:
    if k not in converter:
        converter[k] = k

for l in clists:
    
    if 'new' not in l:
        print('[i] Analyzing {0}...'.format(l.split('/')[-1]))
        clist = load_conceptlist(l)
        for k,entry in clist.items():
            
            if k not in ['header', 'splits', 'mergers']:

                # replace concepticon_id with real gloss
                if 'CONCEPTICON_ID' in entry:
                    
                    if entry['CONCEPTICON_ID']:
                        if entry['CONCEPTICON_ID'] != converter[entry['CONCEPTICON_ID']]:
                            print(concepticon[entry['CONCEPTICON_ID']][1],
                                    concepticon[converter[entry['CONCEPTICON_ID']]][1],
                                    entry['CONCEPTICON_ID'],
                                    converter[entry['CONCEPTICON_ID']]
                                    )
                        entry['CONCEPTICON_ID'] = converter[entry['CONCEPTICON_ID']]
                        entry['CONCEPTICON_GLOSS'] = concepticon[entry['CONCEPTICON_ID']][1]
                    else:
                        entry['CONCEPTICON_GLOSS'] = ''

        
        
        if 'nonew' in argv:
            write_conceptlist(clist, l)
        else:
            write_conceptlist(clist, l.replace('.tsv','.new.tsv'))
        print('... wrote concept list {0}.'.format(l.split('/')[-1]))
