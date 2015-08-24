"""
Simple helper script to extract data from the unified lego concepticon
"""
import re

data = open('Lego-Unified.rdf').read()

concepts = re.findall(
        '<gold:SemanticUnit[^>]*>.*?</gold:SemanticUnit>',
        data,
        re.DOTALL
        )

lines = []
idx = 1
for concept in sorted(concepts, key=lambda x: int(re.findall(
    '<gold:SemanticUnit.*?http://.*?/([0-9]*)"', x)[0])):
    
    
    #print(concept.split('\n')[0])
    curl = re.findall('<gold:SemanticUnit[^>]*"(http://[^"]*)">', concept)[0]
    cid = curl.split('/')[-1]

    # get the links
    wold = re.findall('<owl:sameAs rdf:resource="([^"]*)"', concept)
    if wold:
        wold = wold[0].split('/')[-1]
    else:
        print("no wold for {0}".format(concept.split('\n')[0]))
        wold = ''

    # get the usher id
    uid = re.findall('concept/([0-9]*?)/uw', concept)
    uid = uid[0] if uid else ''

    label = re.findall('<skos:prefLabel>(.*?)</skos:prefLabel>', concept)
    if label:
        label = label[0]
        lines += [[str(idx), cid, label, curl, wold, uid]]
        idx += 1


with open('../unlinked/Good-2010-{0}.tsv'.format(len(concepts)), 'w') as f:
    f.write('NUMBER\tLEGO_ID\tENGLISH\tWOLD\tUSHER_WHITEHOUSE\n')
    for line in lines:
        f.write('\t'.join(line)+'\n')




print(len(concepts))
