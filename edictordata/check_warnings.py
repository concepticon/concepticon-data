from concepticondata.util import *

from glob import glob

files = glob('../concepticondata/conceptlists/*.tsv')
splits = 0
entries = 0
mergers = 0
for f in sorted(files):

    idf = f.split('/')[-1].replace('.tsv','')

    clist = load_conceptlist(f)
    
    
    split_status = len(clist['splits'])
    merger_status = len(clist['mergers'])
   
    if merger_status:
        mrg = []
        for m in clist['mergers']:
            d
        status = 'has {0} splits and {1} mergers.'.format(split_status,
                merger_status)
        print('[i] Conceptlist {0} {1}'.format(idf,status))
    
    # add general count on mergers and splits
    splits += len(clist['splits'])
    mergers += len(clist['mergers'])
    entries += len(clist) - 2

print(splits,mergers,entries)


