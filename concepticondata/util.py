import os
import csv
import shutil
import re

import concepticondata


ID_SEP_PATTERN = re.compile('\.|,|;')


def unique(iterable):
    return list(sorted(set(i for i in iterable if i)))


def split_ids(s):
    return unique(id_.strip() for id_ in ID_SEP_PATTERN.split(s) if id_.strip())


def data_path(*comps):
    return os.path.join(os.path.dirname(concepticondata.__file__), *comps)


def tsv_items(path):
    items = []
    with open(path) as csvfile:
        for item in csv.DictReader(csvfile, delimiter='\t'):
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

