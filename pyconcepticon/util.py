from __future__ import unicode_literals
import re
from collections import defaultdict, OrderedDict, Counter
from functools import partial
from operator import attrgetter

from clldutils import jsonlib
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


def read_all(fname, **kw):
    kw.setdefault('delimiter', '\t')
    if not kw.get('dicts'):
        kw.setdefault('namedtuples', True)
    return list(dsv.reader(fname, **kw))


def read_dicts(fname, schema=None, **kw):
    kw['dicts'] = True
    res = read_all(fname, **kw)
    if schema:
        def identity(x):
            return x
        colspec = {}
        for col in schema['columns']:
            conv = {
                'integer': int,
                'float': float,
            }.get(col['datatype'])
            colspec[col['name']] = conv or identity
        res = [{k: colspec[k](v) for k, v in d.items()} for d in res]
    return res


class UnicodeWriter(dsv.UnicodeWriter):
    def __init__(self, *args, **kw):
        kw.setdefault('delimiter', '\t')
        self._rownum = None
        super(UnicodeWriter, self).__init__(*args, **kw)

    def writerow(self, row):
        if self._rownum is None:
            self._rownum = len(row)
        dsv.UnicodeWriter.writerow(self, row)

    def writeblock(self, rows, start='#<<<', end='#>>>'):
        assert self._rownum
        self.writerow([start] + (self._rownum - 1) * [''])
        for row in rows:
            self.writerow(row)
        self.writerow([end] + (self._rownum - 1) * [''])


def lowercase(d):
    return {k.lower(): v for k, v in d.items()}


def unique(iterable):
    return list(sorted(set(i for i in iterable if i)))


def split(s, sep=','):
    return unique(ss.strip() for ss in s.split(sep) if ss.strip())


def split_ids(s):
    return unique(id_.strip() for id_ in ID_SEP_PATTERN.split(s) if id_.strip())


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


class SourcesCatalog(object):
    def __init__(self, path):
        self.path = path
        self.items = jsonlib.load(self.path) if self.path.exists() else {}

    def __contains__(self, item):
        return item in self.items

    def get(self, item):
        return self.items.get(item)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        jsonlib.dump(
            OrderedDict([(k, OrderedDict([i for i in sorted(v.items())]))
                         for k, v in sorted(self.items.items())]),
            self.path,
            indent=4)

    def add(self, key, obj):
        bsid = obj.bitstreams[0].id
        self.items[key] = OrderedDict([
            ('url', 'https://cdstar.shh.mpg.de/bitstreams/{0}/{1}'.format(obj.id, bsid)),
            ('objid', obj.id),
            ('original', bsid),
            ('size', obj.bitstreams[0].size),
            ('mimetype', obj.bitstreams[0].mimetype),
        ])
        return self.items[key]
