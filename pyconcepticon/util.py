from __future__ import unicode_literals
import re
from collections import defaultdict
from functools import partial

from clldutils.path import Path
from clldutils import dsv

import pyconcepticon


REPOS_PATH = Path(pyconcepticon.__file__).parent.parent
PKG_PATH = Path(pyconcepticon.__file__).parent
ID_SEP_PATTERN = re.compile('\.|,|;')

rewrite = partial(dsv.rewrite, delimiter='\t')


def reader(fname, **kw):
    kw.setdefault('delimiter', '\t')
    if not kw.get('dicts'):
        kw.setdefault('namedtuples', True)
    return dsv.reader(fname, **kw)


def read_one(fname, **kw):
    for item in reader(fname, **kw):
        return item


def read_all(fname, **kw):
    return list(reader(fname, **kw))


read_dicts = partial(read_all, dicts=True)


class UnicodeWriter(dsv.UnicodeWriter):
    def __init__(self, **kw):
        kw.setdefault('delimiter', '\t')
        super(UnicodeWriter, self).__init__(**kw)


def unique(iterable):
    return list(sorted(set(i for i in iterable if i)))


def split_ids(s):
    return unique(id_.strip() for id_ in ID_SEP_PATTERN.split(s) if id_.strip())


def data_path(*comps, **kw):
    return kw.get('repos', REPOS_PATH).joinpath('concepticondata', *comps)


def listdir(name, **kw):
    return sorted(data_path(name, **kw).glob('*.tsv'), key=lambda p: p.name)


conceptlists = partial(listdir, 'conceptlists')
concept_set_meta = partial(listdir, 'concept_set_meta')


def visit(visitor, fname):
    return rewrite(fname, visitor)


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
    data = read_dicts(idf)
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


def natural_sort(l):
    """
    Code-piece from
    http://stackoverflow.com/questions/4836710/does-python-have-a-built-in-function-for-string-natural-sort
    """
    def convert(text):
        return int(text) if text.isdigit() else text.lower()

    def alphanum_key(key):
        return [convert(c) for c in re.split('([0-9]+)', key)]

    return sorted(l, key=alphanum_key)


def write_conceptlist(clist, filename, header=False):
    """
    Write conceptlist to file.
    """
    header = header or clist['header']
    keys = natural_sort(list(clist.keys()))
    with UnicodeWriter(filename) as writer:
        writer.writerow(header)
        for k in keys:
            v = clist[k]
            if k not in ['splits', 'mergers', 'header']:
                writer.writerow([v[h] for h in header])
