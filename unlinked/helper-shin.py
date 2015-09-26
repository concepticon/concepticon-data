# author   : Johann-Mattis List
# email    : mattis.list@uni-marburg.de
# created  : 2015-06-25 11:07
# modified : 2015-06-25 11:07
"""
<++>
"""

__author__="Johann-Mattis List"
__date__="2015-06-25"

from lingpyd import *

csv = csv2list('shin-test.txt', strip_lines=False)

tmp = []
out = []
start = ''
idx = 0
items = ['' for x in range(9)]
for line in csv:

    nline = [a for a in line] + ['' for x in range(9)]
    nline = nline[:10]

    if nline[-1]:
        items[-1] = nline[-1]
        out += [[x for x in items]]
    else:
        count = nline[0].split('.')[0]
        for i,itm in enumerate(items[:-1]):
            if nline[i]:
                items[i] = nline[i]
            elif not itm.startswith(count):
                items[i] = nline[i]


output = []
idx = 1
for line in out:
    items = line[-1][2:].replace(' usw.','').split(', ')
    for itm in items:
        if itm.strip():
            output += [[str(idx),itm.replace(',',''),' > '.join([x for x in line[:-1] if x])]]
            idx += 1
with open('Shin-1995-{0}.tsv'.format(idx-1),'w') as f:
    f.write('ID\tNUMBER\tGLOSS\tHIERARCHY\n')
    for line in output:
        sid = 'Shin-1995-{0}-{1}'.format(idx-1, line[0])
        f.write('\t'.join([sid]+line)+'\n')
