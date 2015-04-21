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

clists = glob('../concepticondata/conceptlists/*.tsv')
concepticon = dict([(a,b) for a,*b in csv2list('../concepticondata/concepticon.tsv',
    strip_lines=False)])


for l in clists:

    if 'new' not in l:

        clist = load_conceptlist(l)
        for k,entry in clist.items():
            
            if k not in ['header', 'splits', 'mergers']:

                # replace concepticon_id with real gloss
                if 'CONCEPTICON_ID' in entry:
                    if entry['CONCEPTICON_ID']:
                        entry['CONCEPTICON_GLOSS'] = concepticon[entry['CONCEPTICON_ID']][1]
                    else:
                        entry['CONCEPTICON_GLOSS'] = ''
        
        if 'nonew' in argv:
            write_conceptlist(clist, l)
        else:
            write_conceptlist(clist, l.replace('.tsv','.new.tsv'))
        print('Wrote concept list {0}.'.format(l.split('/')[-1]))
