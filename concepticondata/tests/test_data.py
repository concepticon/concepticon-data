import os
import re
import io
import glob
import warnings

from concepticondata.util import data_path, tsv_items, split_ids


SUCCESS = True
BIB_ID_PATTERN = re.compile('@[a-zA-Z]+\{(?P<id>[^,]+),')


def error(msg, name, line=''):
    global SUCCESS
    SUCCESS = False
    if line:
        line = ':%s' % line
    print('ERROR:%s%s: %s' % (name, line, msg))

def warning(msg, name, line=''):
    if line:
        line = ':%s' % line
    warnings.warn('WARNING:%s%s: %s' % (name, line, msg), Warning)


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
                error('non-unique %s: %s' % (unique, row[unique]), path, line)
            uniquevalues.add(row[unique])
        rows.append((line, row))
    return rows

def read_sources(path):

    infiles = glob.glob(os.path.join(path, '*.pdf'))

    return [os.path.split(f)[-1][:-4] for f in infiles]


def test():
    conceptlists = {n: read_tsv(data_path('conceptlists', n), unique=None) for n in os.listdir(data_path('conceptlists')) if not n.startswith('.')}

    read_tsv(data_path('concepticon.tsv'))
    concepticon = read_tsv(data_path('concepticon.tsv'), unique='GLOSS')

    refs = set()
    with io.open(data_path('references', 'references.bib'), encoding='utf8') as fp:
        for line in fp:
            match = BIB_ID_PATTERN.match(line.strip())
            if match:
                refs.add(match.group('id'))

    #
    # Make sure only records in the BibTeX file references.bib are referenced by
    # concept lists.
    clmd = data_path('conceptlists.tsv')
    clids = []
    visited = []
    for i, cl in read_tsv(clmd):
        clids.append(cl['ID'])
        for ref in split_ids(cl['REFS']):
            if ref not in refs and ref not in visited:
                error('unknown bibtex record "%s" referenced' % ref, clmd, i)
                visited += [ref]

    #
    # make also sure that all sources are accompanied as pdf, but only write a
    # warning if this is not the case
    #
    pdfs = read_sources('sources')
    short_path = os.path.split(clmd)[1]
    for i, cl in read_tsv(clmd):
        for ref in split_ids(cl['REFS']):
            if ref not in pdfs:

                warning('no source found for bibtex record "%s" ' % ref,
                        short_path, i)


    ref_cols = {
        'CONCEPTICON_ID': set(cs[1]['ID'] for cs in concepticon),
        'CONCEPTICON_GLOSS': set(cs[1]['GLOSS'] for cs in concepticon),
    }

    for name, concepts in conceptlists.items():
        print(name)
        assert name.replace('.tsv', '') in clids

        missing = []
        for line, concept in concepts:
            for col, values in ref_cols.items():
                if col not in concept:
                    if col not in missing:
                        error('missing column %s' % col, name)
                        missing.append(col)
                elif concept[col] and concept[col] not in values:
                    error('invalid value for %s: %s' % (col, concept[col]), name, line)

    if not SUCCESS:
        raise ValueError('integrity checks failed!')
