import os
import csv
import shutil
import re
from collections import defaultdict, OrderedDict

import concepticondata


ID_SEP_PATTERN = re.compile('\.|,|;')


def unique(iterable):
    return list(sorted(set(i for i in iterable if i)))


def split_ids(s):
    return unique(id_.strip() for id_ in ID_SEP_PATTERN.split(s) if id_.strip())


def data_path(*comps):
    return os.path.join(os.path.dirname(concepticondata.__file__), *comps)


def tsv_items(path, ordered=False):
    items = []
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for item in reader:
            if ordered:
                item = OrderedDict([(k, item[k]) for k in reader.fieldnames])
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
        A dictionary with IDs as keys and OrderedDicts with the data from the row as
        values. Duplicate links are passed as "splits" in a specific entry of the
        dictionary (named "splits").
    """
    data = tsv_items(idf, ordered=True)
    if data:
        clist = dict(header=list(data[0].keys()), splits=[], mergers=[])
        cidxs = defaultdict(list)

        previous_item = None
        for item in data:
            if item['ID'] and item['ID'] not in clist:
                previous_item = clist[item['ID']] = item
            else:
                # a concept without ID or with duplicate ID
                if previous_item:
                    # complete data in item with that of the previous one (?)
                    for k, v in previous_item.items():
                        if not item[k]:
                            item[k] = v
                    clist['splits'].append(item)
                else:
                    raise ValueError("item {0} is wrong".format(item))
            cidxs[previous_item['CONCEPTICON_ID']].append(previous_item['ID'])

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
