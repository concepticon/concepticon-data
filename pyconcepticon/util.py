from __future__ import unicode_literals
import re
from collections import defaultdict, OrderedDict, Counter
from functools import partial
from operator import attrgetter

from tabulate import tabulate
from clldutils.path import Path
from clldutils import dsv

import pyconcepticon

REPOS_PATH = Path(pyconcepticon.__file__).parent.parent
PKG_PATH = Path(pyconcepticon.__file__).parent
ID_SEP_PATTERN = re.compile('\.|,|;')
PREFIX = 'CONCEPTICON'
CS_GLOSS = PREFIX + '_GLOSS'
CS_ID = PREFIX + '_ID'

rewrite = partial(dsv.rewrite, delimiter='\t')


def to_dict(iterobjects, key=attrgetter('id')):
    """
    Turns an iterable into an `OrderedDict` mapping unique keys to items.

    :param iterobjects: an iterable to be turned into the values of the dictionary.
    :param key: a callable which creates a key from an item.
    :returns: `OrderedDict`
    """
    res, keys = OrderedDict(), Counter()
    for obj in iterobjects:
        k = key(obj)
        res[k] = obj
        keys.update([k])
    if keys:
        k, n = keys.most_common(1)[0]
        if n > 1:
            raise ValueError('non-unique key: %s' % k)
    return res


class MarkdownTable(list):
    def __init__(self, *cols):
        self.columns = list(cols)
        list.__init__(self)

    def render(
            self, fmt='pipe', sortkey=None, condensed=True, verbose=False, reverse=False):
        res = tabulate(
            sorted(self, key=sortkey, reverse=reverse) if sortkey else self,
            self.columns,
            fmt,
            floatfmt='.2f')
        if fmt == 'pipe':
            if condensed:
                # remove whitespace padding around column content:
                res = re.sub('\|[ ]+', '| ', res)
                res = re.sub('[ ]+\|', ' |', res)
            if verbose:
                res += '\n\n(%s rows)\n\n' % len(self)
        return res


def read_all(fname, **kw):
    kw.setdefault('delimiter', '\t')
    if not kw.get('dicts'):
        kw.setdefault('namedtuples', True)
    return list(dsv.reader(fname, **kw))


read_dicts = partial(read_all, dicts=True)


class UnicodeWriter(dsv.UnicodeWriter):
    def __init__(self, *args, **kw):
        kw.setdefault('delimiter', '\t')
        super(UnicodeWriter, self).__init__(*args, **kw)


def lowercase(d):
    return {k.lower(): v for k, v in d.items()}


def unique(iterable):
    return list(sorted(set(i for i in iterable if i)))


def split(s, sep=','):
    return unique(ss.strip() for ss in s.split(sep) if ss.strip())


def split_ids(s):
    return unique(id_.strip() for id_ in ID_SEP_PATTERN.split(s) if id_.strip())


def data_path(*comps, **kw):
    return kw.get('repos', REPOS_PATH).joinpath('concepticondata', *comps)


def visit(visitor, fname):
    return rewrite(fname, visitor)


def load_conceptlist(idf):
    """
    Load a concept list and display it as a complex dictionary (json-style).

    :rtype: dict /
        A dictionary with IDs as keys and OrderedDicts with the data from the row as /
        values. Duplicate links are passed as "splits" in a specific entry of the /
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
                else:  # pragma: no cover
                    raise ValueError("item {0} is wrong".format(item))
            cidxs[previous_item[CS_ID]].append(previous_item['ID'])

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
