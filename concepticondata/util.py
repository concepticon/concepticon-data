from __future__ import unicode_literals
import re
from collections import defaultdict

from clldutils.path import Path
from clldutils.dsv import reader, UnicodeWriter, rewrite

import concepticondata


PKG_PATH = Path(concepticondata.__file__).parent
ID_SEP_PATTERN = re.compile('\.|,|;')


def unique(iterable):
    return list(sorted(set(i for i in iterable if i)))


def split_ids(s):
    return unique(id_.strip() for id_ in ID_SEP_PATTERN.split(s) if id_.strip())


def data_path(*comps):
    return PKG_PATH.joinpath(*comps).as_posix()


def tsv_items(path, ordered=False):
    return list(reader(path, delimiter='\t', dicts=True))


def visit(visitor, fname):
    return rewrite(fname, visitor, delimiter='\t')


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
    with UnicodeWriter(filename, delimiter='\t') as writer:
        writer.writerow(header)
        for k in keys:
            v = clist[k]
            if k not in ['splits', 'mergers', 'header']:
                writer.writerow([v[h] for h in header])
