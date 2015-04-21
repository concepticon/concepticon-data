"""refine concept relations"""

import networkx as nx
import lingpy

G = nx.DiGraph()

relations = dict(
    broader = 'narrower',
    similar = 'similar',
    sameas = 'sameas',
    resultof = 'resultsin',
    produces = 'producedby',
    usedfor = 'requires',
    consistsof = '',
    classof = 'instanceof',
    intransitiveof = 'transitiveof'
        )
for k,v in list(relations.items()):
    if v and v != k:
        relations[v] = k

# load teh concepticon to get the meta-data
_C = lingpy.csv2list('concepticon.tsv')
C = {}
for line in _C[1:]:
    tmp = dict(zip([x.lower() for x in _C[0]],line))
    C[line[0]] = tmp

with open('conceptrelations.tsv') as f:

    for line in f.readlines()[1:]:
        
        a,b,c = [x.strip() for x in line.split('\t')]
        
        if a and b and relations[b]:
            G.add_edge(a,c,relation=b)
            G.add_edge(c,a,relation=relations[b])

for node,data in G.nodes(data=True):
    data['label'] = C[node]['gloss']
    data['cid'] = C[node]['id']

nx.write_gml(G, 'conceptrelations.gml')
with open('conceptrelations.tsv', 'w') as f:
    
    f.write('SOURCE\tRELATION\tTARGET\n')
    for a,b,d in G.edges(data=True):
        
        f.write('{0}\t{2}\t{1}\n'.format(a,b,d['relation']))
