from lingpy import *
import networkx as nx

G = nx.read_gml('clics.gml')
degree = nx.degree(G, weight='family')

degs = {}
for k,v in degree.items():
    degs[G.node[k]['key']] = (
            G.node[k]['frequency'],
            degree[k])


ids = csv2list('Key-2015-1310.tsv', strip_lines=False)
wld = csv2list('Haspelmath-2009-1460.tsv', strip_lines=False)

# make dict of wold
wlD = dict(
        [(line[5],(line[1],line[2])) for line in wld])

n2c = csv2dict('nodes2communities.csv')
n2s = csv2dict('nodes2cuts.csv')

clics = [[
    'ID',
    'CONCEPTICON_ID',
    'CONCEPTICON_GLOSS',
    'NUMBER',
    'ENGLISH',
    'COMMUNITY_LABEL',
    'COMMUNITY_ID',
    'COMMUNITY_URL',
    'NETWORK_ID'
    'NETWORK_URL',
    'FREQUENCY',
    'DEGREE',
    ]]
idx = 1
for k in sorted(n2c):
    nk = k.replace('.','-')
    gloss = n2c[k][0]
    url1 = 'http://clics.lingpy.org/browse.php?community={0}'.format(n2c[k][2])
    url2 = 'http://clics.lingpy.org/browse.php?community={0}&view=part'.format(n2s[k][2])
    ck = n2c[k][-1]

    if 'zero' in gloss:
        nk = '13'
    if gloss == 'ten': 
        nk = '13-1'
    if nk not in wlD:
        nk = k.split('.')[0]+'-0'+k.split('.')[1]
        

    if nk in wlD:
        cid,cgl = wlD[nk]
        clics += [
                [
                    'List-2014-1280-{0}'.format(idx),
                    cid,
                    cgl,
                    str(idx),
                    gloss,
                    ck,
                    n2c[k][1],
                    url1,
                    n2s[k][1],
                    url2,
                    str(degs[k][0]),
                    str(degs[k][1])
                    ]]
        idx += 1
    else:
        print('no id found for "{0} / {1}"'.format(k,gloss))
with open('List-2014-1280.tsv', 'w') as f:
    for line in clics:
        f.write('\t'.join(line)+'\n')

# add stuff to ids
#for i,line in enumerate(ids[1:]):
#    
#    try:
#        gls,idx = wlD[line[3].strip('0')]
#    except KeyError:
#        try:
#            pre,post = line[3].split('-')
#            ngl = pre + '-' + post[::-1]
#            gls,idx = wlD[ngl]
#        except KeyError:
#            if line[1] == 'zero, nothing':
#                gls,idx = wlD['13']
#            elif 'tree' in line[1]:
#                gls,idx = wlD['8-6']
#            else:
#                gls,idx = '???','???'
#                print('problem with', line[1],line[3])
#    ids[i+1] += [gls,idx]
#
#ids[0] += ['CONCEPTICON_ID', 'CONCEPTICON_GLOSS']
#
#with open('Key-2015-1310.mapped.tsv','w') as f:
#    for line in ids:
#        f.write('\t'.join(line)+'\n')





