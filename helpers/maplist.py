# author   : Johann-Mattis List
# email    : mattis.list@uni-marburg.de
# created  : 2015-04-21 14:09
# modified : 2015-04-21 14:09
"""
Map a concept list with the data in the concepticon.
"""

__author__="Johann-Mattis List"
__date__="2015-04-21"

# this version uses a temporarl lingpy path, change it to "lingpy", instead of
# "lingpyd", but make sure to use the most recent version of lingpy
from concepticondata import *
from lingpyd.meaning.glosses import *
from lingpyd import *
import sys

# we need a file and stop if we don't get one
if len(sys.argv) < 2:
    print("NO FILE SPECIFIED")
    sys.exit()

# path for concepticon-base-list
cpath = '../concepticondata/concepticon.tsv'

# we will allow for a third argument to provide the respective conceptlist as
# base-list
if len(sys.argv) >= 3:
    bpath = "../concepticondata/conceptlists/"+sys.argv[2]+'.tsv'
    baselist = csv2list(bpath)
    
    # find the concepticon-id
    h = baselist[0].index('CONCEPTICON_ID')
    concepts = [line[h] for line in baselist[1:]]

elif len(sys.argv) == 2:
    bpath = cpath 
    baselist = csv2list(bpath)
    # find the concepticon-id
    h = 0 #baselist[0].index('CONCEPTICON_ID')
    concepts = [line[h] for line in baselist[1:]]
else:
    print("Too many arguments specified!")
    sys.exit()


# create a temporary file from concepticon.tsv
ccc = csv2list(cpath)
with open('.temporary1.tsv', 'w') as f:
    f.write('NUMBER\tGLOSS\n')
    for line in ccc[1:]:
        if line[0] in concepts:
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

print("[i] Created temporary file from the current concepticon.")
# create a temporary file from the input list
ipt = csv2list(sys.argv[1])
if 'NUMBER' not in ipt[0] and not ('GLOSS' in ipt[0] or 'ENGLISH' in ipt[0]):
    print('NO NUMBER OR GLOSS COULD BE FOUND')
    sys.exit()
# redefine gloss-name to "ENGLISH" if we don't find it
elif not 'GLOSS' in ipt[0]:
    gloss = 'ENGLISH'
else:
    gloss = "GLOSS"


if not "swap" in sys.argv:
compare_conceptlists('.temporary1.tsv', sys.argv[1], output='tsv',
        filename=sys.argv[1].replace('.tsv', '.mapped.tsv'), debug=True,
        gloss=gloss)
print("[i] successfully mapped the lists.")
        
