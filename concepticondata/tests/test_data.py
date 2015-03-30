import os
import re
import io

from concepticondata.util import data_path, tsv_items, split_ids


SUCCESS = True
BIB_ID_PATTERN = re.compile('@[a-zA-Z]+\{(?P<id>[^,]+),')


def error(msg, name, line=''):
    global SUCCESS
    SUCCESS = False
    if line:
        line = ':%s' % line
    print('ERROR:%s%s: %s' % (name, line, msg))


def read_tsv(path, unique='ID'):
    uniquevalues = set()
    rows = []
    for line, row in enumerate(tsv_items(path)):
        line += 2
        if unique:
            if unique not in row:
                error('unique key missing: %s' % unique, path, line)
                continue
            if row[unique] in uniquevalues:
                error('non-unique id: %s' % row[unique],path, line)
            uniquevalues.add(row[unique])
        rows.append((line, row))
    return rows


def test():
    conceptlists = {n: read_tsv(data_path('conceptlists', n), unique=None) for n in os.listdir(data_path('conceptlists')) if not n.startswith('.')}

    concepticon = read_tsv(data_path('concepticon.tsv'), unique='OMEGAWIKI')

    refs = set()
    with io.open(data_path('references', 'references.bib'), encoding='utf8') as fp:
        for line in fp:
            match = BIB_ID_PATTERN.match(line.strip())
            if match:
                refs.add(match.group('id'))
    
    if not SUCCESS:
        raise ValueError('integrity checks failed!')

