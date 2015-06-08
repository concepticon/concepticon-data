from concepticondata.util import *

from glob import glob

files = glob('../concepticondata/conceptlists/*.tsv')
splits = 0
entries = 0
mergers = 0
for f in [x for x in sorted(files) if 'mergers' not in x]:
    
    idf = f.split('/')[-1].replace('.tsv','')

    clist = load_conceptlist(f)
    
    
    split_status = len(clist['splits'])
    merger_status = len(clist['mergers'])
   
    if merger_status:

        
        status = 'has {0} splits and {1} mergers.'.format(split_status,
                merger_status)
        print('[i] Conceptlist {0} {1}'.format(idf,status))
        
        mcount = 1
        for line in clist['mergers']:
            for m in line:
                clist[m]['MERGER'] = str(mcount)
            mcount += 1


        for k in [k for k in clist.keys() if k not in
                ['header','mergers','splits']]:
            if k not in ['mergers','splits']:
                if not 'MERGER' in clist[k]:
                    clist[k]['MERGER'] = ''
        write_conceptlist(clist, f.replace('.tsv', '.mergers.tsv'), 
                header=['MERGER']+clist['header'])
    
    # add general count on mergers and splits
    splits += len(clist['splits'])
    mergers += len(clist['mergers'])
    entries += len(clist) - 2

print(splits,mergers,entries)


