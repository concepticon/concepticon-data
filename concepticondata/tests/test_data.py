from __future__ import unicode_literals
import os
import re
import io
import glob
import warnings
from collections import namedtuple

from clldutils.misc import normalize_name

from concepticondata.util import data_path, tsv_items, split_ids, PKG_PATH

SUCCESS = True
BIB_ID_PATTERN = re.compile('@[a-zA-Z]+\{(?P<id>[^,]+),')
NUMBER_PATTERN = re.compile('(?P<number>[0-9]+)(?P<suffix>.*)')


def split(s, sep=','):
    return [ss.strip() for ss in s.split(sep) if ss.strip()]


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
    sources = [os.path.split(f)[-1][:-4] for f in infiles]
    return sources


def test():
    conceptlists = {
        cl.name: read_tsv(cl, unique=None)
        for cl in PKG_PATH.joinpath('conceptlists').glob('*.tsv')
        if not cl.stem.startswith('.')}

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
    clids = {}
    visited = []
    for i, cl in read_tsv(clmd):
        clids[cl['ID']] = cl
        for ref in split_ids(cl['REFS']):
            if ref not in refs and ref not in visited:
                error('unknown bibtex record "%s" referenced' % ref, clmd, i)
                visited += [ref]

    #
    # make also sure that all sources are accompanied as pdf, but only write a
    # warning if this is not the case
    #
    pdfs = read_sources(data_path('sources'))
    no_pdf_for_source = []
    for i, cl in read_tsv(clmd):
        for ref in split_ids(cl['PDF']):
            if ref not in pdfs:
                no_pdf_for_source += [ref]
    
    if no_pdf_for_source:
        warning(
            '\n'.join(no_pdf_for_source),
            'no pdf found for {0} sources'.format(len(no_pdf_for_source)))
    
    ref_cols = {
        'CONCEPTICON_ID': set(cs[1]['ID'] for cs in concepticon),
        'CONCEPTICON_GLOSS': set(cs[1]['GLOSS'] for cs in concepticon),
    }

    for name, concepts in conceptlists.items():
        try:
            cl = clids[name.replace('.tsv', '')]
        except KeyError:
            error('unkown record {0} referenced'.format(name), '', '')
            cl = {}

        missing = []
        for i, (line, concept) in enumerate(concepts):
            if i == 0:
                cols = list(concept.keys())
                try:
                    namedtuple('nt', [normalize_name(n) for n in cols])
                except ValueError as e:
                    error('%s' % e, name, line)
                for lg in split(cl.get('SOURCE_LANGUAGE', [])):
                    if lg.upper() not in cols:
                        error('missing source language col %s' % lg.upper(), name, '')
            if not NUMBER_PATTERN.match(concept['NUMBER']):
                error('invalid concept NUMBER %(NUMBER)s' % concept, name, line)
            for col, values in ref_cols.items():
                if col not in concept:
                    if col not in missing:
                        error('missing column %s' % col, name)
                        missing.append(col)
                elif concept[col] and concept[col] not in values:
                    error('invalid value for %s: %s' % (col, concept[col]), name, line)

    if not SUCCESS:
        raise ValueError('integrity checks failed!')
