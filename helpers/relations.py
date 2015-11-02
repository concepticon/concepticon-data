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
_C = lingpy.csv2list('../concepticondata/concepticon.tsv')
C = {}
for line in _C[1:]:
    tmp = dict(zip([x.lower() for x in _C[0]],line))
    C[line[0]] = tmp

with open('../concepticondata/conceptrelations.tsv') as f:

    for line in f.readlines()[1:]:
        print (line.replace('\t','-x-'))
        
        a,_a,b,c,_c = [x.strip() for x in line.split('\t')]
        
        if a and b and relations[b]:
            G.add_edge(a,c,relation=b)
            G.add_edge(c,a,relation=relations[b])

        G.node[a]['label'] = C[a]
        G.node[c]['label'] = C[c]

for node,data in G.nodes(data=True):
    data['label'] = C[node]['gloss']
    data['cid'] = C[node]['id']

nx.write_gml(G, '../concepticondata/conceptrelations.gml')
with open('../concepticondata/conceptrelations.modified.tsv', 'w') as f:
    
    f.write('SOURCE\tSOURCE_GLOSS\tRELATION\tTARGET\tTARGET_GLOSS\n')
    for a,b,d in G.edges(data=True):
        
        f.write('{0}\t{1}\t{2}\t{3}\t{4}\n'.format(
            a,
            G.node[a]['label'],
            d['relation'],
            b,
            G.node[b]['label']
            ))
