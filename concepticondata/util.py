import os
import csv
import shutil
import re
from collections import defaultdict

import concepticondata


ID_SEP_PATTERN = re.compile('\.|,|;')


def unique(iterable):
    return list(sorted(set(i for i in iterable if i)))


def split_ids(s):
    return unique(id_.strip() for id_ in ID_SEP_PATTERN.split(s) if id_.strip())


def data_path(*comps):
    return os.path.join(os.path.dirname(concepticondata.__file__), *comps)


def tsv_items(path, reader=None):
    reader = reader or csv.DictReader
    items = []
    with open(path) as csvfile:
        for item in reader(csvfile, delimiter='\t'):
            items.append(item)
    return items


def visit(visitor, fname):
    """Utility function to rewrite rows in tsv files.

    :param visitor: A callable that takes a row as input and returns a (modified) row or\
    None to filter out the row.
    """
    tmp = os.path.join(os.path.dirname(fname), '.' + os.path.basename(fname))
    with open(fname, 'rb') as source:
        with open(tmp, 'wb') as target:
            writer = csv.writer(target, delimiter='\t')
            for i, row in enumerate(csv.reader(source, delimiter='\t')):
                row = visitor(i, row)
                if row:
                    writer.writerow(row)
    shutil.move(tmp, fname)


def load_conceptlist(idf):
    """
    Load a concept list and display it as a complex dictionary (json-style).

    Returns
    -------
    clist : dict
        A dictionary with IDs as keys and a dictionary with column header
        values as keys of the secondary dictionary. Duplicate links are passed
        as "warnings" in a specific entry of the dictionary (named "warnings").
    """
    data = tsv_items(idf, csv.reader)

    # make a dictionary, store secondary stuff in warning set
    warnings = []

    header = data.pop(0)

    cidxs = defaultdict(list)
    clist = {'header': header}

    preline = {}
    for line in data:
        if line[0] and line[0] not in clist:
            clist[line[0]] = dict(zip(header, line))
            preline = clist[line[0]]
        else:
            if preline:
                newline = dict(zip(header, line))
                for k, v in preline.items():
                    if not newline[k]:
                        newline[k] = v
                warnings += [newline]
            else:
                raise ValueError("line {0} is wrong".format(line))
        cidxs[preline['CONCEPTICON_ID']].append(preline['ID'])

    clist['splits'] = warnings
    clist['mergers'] = [cidxs[k] for k in cidxs if len(cidxs[k]) > 1]
    return clist


def write_conceptlist(clist, filename, header=False):
    """
    Write conceptlist to file.
    """
    def natural_sort(l): 
        """
        Code-piece from
        http://stackoverflow.com/questions/4836710/does-python-have-a-built-in-function-for-string-natural-sort
        """
        convert = lambda text: int(text) if text.isdigit() else text.lower() 
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(l, key=alphanum_key)
    
    header = header or clist['header']
    keys = natural_sort(list(clist.keys()))
    with open(filename, 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(header)
        for k in keys: 
            v = clist[k]
            if k not in ['splits', 'mergers', 'header']:
                writer.writerow([v[h] for h in header])
