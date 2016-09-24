# author   : Johann-Mattis List
# email    : mattis.list@uni-marburg.de
# created  : 2015-04-21 09:15
# modified : 2015-04-21 09:15
"""
Refine the data by replacing glosses by the concepticon.tsv glosses.
"""

__author__="Johann-Mattis List"
__date__="2015-04-21"

from pyconcepticon.util import load_conceptlist, write_conceptlist
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

cid, cgl, gls = 'CONCEPTICON_ID', 'CONCEPTICON_GLOSS', 'ENGLISH'

# assemble modifications for glosses
_mods = csv2list('mods.tsv', strip_lines=False)
mods = {}
for line in _mods[1:]:
    tmpcid = line[1].split(',')[0]
    mods[line[0],tmpcid] = dict(
            source = [x.upper() for x in line[1].split(',')],
            target = [x.upper() for x in line[2].split(',')],
            ignore = line[3].split(',')
            )

    mid,mig = mods[line[0],tmpcid]['target']
    if concepticon[mid][0] != mig:
        raise ValueError('Wrong modification request for {0} and {1} in gloss {2}'.format(
            mid, mig, line[0]))

for l in clists:
    
    if 'new' not in l:
        print('[i] Analyzing {0}...'.format(l.split('/')[-1]))
        clist = load_conceptlist(l)
        clist_name = l.split('/')[-1][:-4]
        for k,entry in clist.items():
            
            if k not in ['header', 'splits', 'mergers']:

                # replace concepticon_id with real gloss
                if 'CONCEPTICON_ID' in entry:
                    
                    if entry['CONCEPTICON_ID']:
                        if entry['CONCEPTICON_ID'] != converter[entry['CONCEPTICON_ID']]:
                            print(concepticon[entry['CONCEPTICON_ID']][0],
                                    concepticon[converter[entry['CONCEPTICON_ID']]][0],
                                    entry['CONCEPTICON_ID'],
                                    converter[entry['CONCEPTICON_ID']]
                                    )
                        entry['CONCEPTICON_ID'] = converter[entry['CONCEPTICON_ID']]
                        entry['CONCEPTICON_GLOSS'] = concepticon[entry['CONCEPTICON_ID']][0]
                    else:
                        entry['CONCEPTICON_GLOSS'] = ''

                # if mods in args
                if 'mods' in argv and cid in entry:
                    gname = 'ENGLISH' if 'ENGLISH' in entry else 'GLOSS'
                    if (entry[gname],entry[cid]) in mods:
                        if [entry[cid],entry[cgl]] == mods[entry[gname],entry[cid]]['source']:
                            print('found')
                            if clist_name not in mods[entry[gname],entry[cid]]['ignore']: # != clist_name:
                                q = 'Changing gloss «{0}» in {5} linked to {1}/{2} to {3}/{4}?'.format(
                                        entry[gname],
                                        entry[cid],
                                        entry[cgl],
                                        mods[entry[gname],entry[cid]]['target'][0],
                                        mods[entry[gname],entry[cid]]['target'][1],
                                        clist_name
                                        )
                                answer = input(q+' ')
                                if answer in 'yY':
                                    ccid = entry[cid]
                                    entry[cid] = mods[entry[gname],ccid]['target'][0]
                                    entry[cgl] = mods[entry[gname],ccid]['target'][1]

        
        
        if 'nonew' in argv and not 'test' in argv:
            write_conceptlist(clist, l)
        elif 'test' in argv:
            pass
        else:
            write_conceptlist(clist, l.replace('.tsv','.new.tsv'))
        print('... wrote concept list {0}.'.format(l.split('/')[-1]))
