# author   : Johann-Mattis List
# email    : mattis.list@uni-marburg.de
# created  : 2015-04-21 14:09
# modified : 2015-04-21 14:09
"""
Map a concept list with the data in the concepticon.
"""

__author__="Johann-Mattis List"
__date__="2015-04-21"

from concepticondata import *
from lingpyd.meaning.glosses import *
from lingpyd import *
import sys

if len(sys.argv) < 2:
    print("NO FILE SPECIFIED")
    sys.exit()

# create a temporary file from concepticon.tsv
ccc = csv2list('../concepticondata/concepticon.tsv')
with open('.temporary1.tsv', 'w') as f:
    f.write('NUMBER\tGLOSS\n')
    for line in ccc[1:]:
        if line[-1] == 'Person/Thing':
            pos = ' (noun)'
        elif line[-1] == 'Action/Process':
            pos = ' (verb)'
        elif line[-1] == 'Property':
            pos = ' (adjective)'
        elif line[-1] == 'Classifier':
            pos = ' (classifier)'
        else:
            pos = ''

        f.write(line[0]+'\t'+line[2]+pos+'\n')

# create a temporary file from the input list
ipt = csv2list(sys.argv[1])
if 'NUMBER' not in ipt[0] and 'GLOSS' not in ipt:
    print('NO NUMBER OR GLOSS COULD BE FOUND')
    sys.exit()


compare_conceptlists('.temporary1.tsv', sys.argv[1], output='tsv',
        filename=sys.argv[1].replace('.tsv', '.mapped.tsv'), debug=True)

        
