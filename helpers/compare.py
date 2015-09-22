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
import networkx as nx

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
    

def merge_lists(*lists, output=False):
    """
    Merge two or more concept lists into one single one.
    """
    out = {}
    for lst in lists:
        clist = load_conceptlist(
                '../concepticondata/conceptlists/'+lst+'.tsv'
                )

        gidx = 'ENGLISH' if 'ENGLISH' in clist['header'] else 'GLOSS'
        for k in clist:
            if k not in ['header','splits','mergers']:
                gloss = clist[k][gidx]
                cidx = clist[k]['CONCEPTICON_ID']
                try:
                    out[cidx] += [gloss]
                except KeyError:
                    out[cidx] = [gloss]

    _G = nx.read_gml('../concepticondata/conceptrelations.gml')
    G = nx.Graph()
    for a,b,d in _G.edges(data=True):
        G.add_edge(_G.node[a]['cid'], _G.node[b]['cid'], **d)
    for node in out:
        G.add_node(node)

    # go for connected components
    S = nx.subgraph(G, out)
    comps = list(nx.connected_components(S))
    outdata = []
    C = csv2dict('../concepticondata/concepticon.tsv', strip_lines=False)
    if len(comps) < len(S):
        for comp in comps:
            #for c in comp:
            outdata += [(comp[0],out[comp[0]][0], C[comp[0]][1], ','.join([out[x][0] for x in
                comp[1:]]), ','.join(C[x][1] for x in comp[1:]))]

    if output == 'tsv':
        with open('merger.tsv', 'w') as f:
            for line in sorted(outdata, key=lambda x: x[2]):
                f.write('\t'.join(line)+'\n')
    else:

        return outdata


