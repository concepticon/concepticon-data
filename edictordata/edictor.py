# author   : Johann-Mattis List
# email    : mattis.list@uni-marburg.de
# created  : 2015-03-31 12:03
# modified : 2015-03-31 12:03
"""
<++>
"""

__author__="Johann-Mattis List"
__date__="2015-03-31"

from lingpyd import *
from glob import glob

# get the files
files = glob('../concepticondata/conceptlists/*.tsv') + \
    ['../concepticondata/concepticon.tsv']

# iterate over files and assign IDs. While we don't have the modified IDs, we
# will add a converter for the old ones
ID = {}
idx = 1
for f in files:

    data = csv2list(f, strip_lines=False)
    header = data[0]
    data = data[1:]
    
    if f.endswith('concepticon.tsv'):
        for line in data:
            if line[0] in ID:
                pass
            else:
                ID[line[0]] = idx
                idx += 1
    else:
        for i,line in enumerate(data):
            if line[1] in ID:
                pass
            elif line[1] == 'NAN':
                ID[line[1]] = 0
            else:
                ID[line[1]] = idx
                idx += 1

with open('id_converter','w') as f:
    f.write('\n'.join([str(a)+'\t'+str(b) for a,b in ID.items()]))
print("[i] Created ID converter and saved it to file.")

# now iterate properly
D = {} # stores all data
headers = [] # stores all headers
idx = 1
for f in files:
    data = csv2list(f, strip_lines=False)
    fname = f.split('/')[-1].replace('.tsv','')
    if fname == 'concepticon':
        fname = '0CONCEPTICON'

    header = data[0]

    data = data[1:]
    for line in data:
        tmp = dict(zip(header,line))
        print(len(line),fname)
        if fname != '0CONCEPTICON' and tmp['CONCEPTICON_ID'] == 'NAN':
            print(fname)
        for k,v in list(tmp.items()):
            if k == 'ID' and fname != '0CONCEPTICON':
                tmp['LIST_'+k] = v
                del tmp[k]
            elif k == 'ID' and fname == '0CONCEPTICON':
                tmp['CONCEPTID'] = ID[v]
                del tmp[k]
            elif k == 'CONCEPTICON_ID':
                tmp['CONCEPTID'] = ID[v]
            elif k == 'GLOSS' and fname == '0CONCEPTICON':
                tmp['CONCEPTICON_GLOSS'] = v
            else:
                tmp[k.replace(' ','_')] = v
                headers += [k]

        tmp['CONCEPTLIST'] = fname
        D[idx] = tmp
        idx += 1

print("[i] Created basic dictionary.")

# create the wordlist file
headers = ['LIST_ID','CONCEPTLIST','CONCEPTID']+[h for h in sorted(set(headers)
    ) if h not in ['ID']]

for k in D:
    if not D[k]['CONCEPTID']:
        print(D[k]['CONCEPTICON_ID'],k,D[k]['CONCEPTID'])

    line = [D[k].get(h) if h in D[k] else '' for h in headers]
    D[k] = line
D[0] = [h for h in headers if h not in ['ID']]

print("[i] Created dictionary in wordlist form.")

# make a wordlist object (for easy change)
wl = Wordlist(D, col='conceptlist', row='concept')

# we check now for multiple relations and the like and resolve them more or
# less automatically
R = {}

# get an etymdict representation, makes iteration simpler
etd = wl.get_etymdict(ref='conceptid')

# first check: search for duplicates
for k in etd:
    for entries in [e for e in etd[k] if e]:
        if len(entries) > 1:
            rel = 'narrower'
        else:
            rel = 'similar'
            
        for entry in entries:
            R[entry] = rel

# second check, we go for broader concepts now, that is, unique ids that are
# linked multiple times
for t in wl.cols:

    d = wl.get_dict(col=t)
    for k in d:
        if len(d[k]) > 1:
            for r in d[k]:
                R[r] = 'broader'

# add entries to worldist
wl.add_entries('relations', R, lambda x: x)


wl.output('tsv', filename='concepticon', ignore=['taxa'])

print("[i] Successfully created wordlist view of the data ({0} lines, {1} glosses, {2} lists).".format(
    len(wl),
    wl.height,
    wl.width))

# only for personal use
import os
os.system('cp concepticon.tsv ~/projects/websites/dighl/edictor/data/')

# create sqlite3-app
from lingpyd.plugins.lpserver import lexibase as lb

db = lb.LexiBase('concepticon.tsv', col='conceptlist', row='gloss')
db.create('concepticon', dbase='concepticon.sqlite3')
os.system('cp concepticon.sqlite3 ~/projects/websites/dighl/edictor/triples/')
