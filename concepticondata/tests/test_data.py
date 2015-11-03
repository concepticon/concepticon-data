from __future__ import unicode_literals
import os
import re
import io
import glob
import warnings
import keyword
import unicodedata
from string import ascii_letters, punctuation
from collections import namedtuple

from concepticondata.util import data_path, tsv_items, split_ids

SUCCESS = True
BIB_ID_PATTERN = re.compile('@[a-zA-Z]+\{(?P<id>[^,]+),')
NUMBER_PATTERN = re.compile('(?P<number>[0-9]+)(?P<suffix>.*)')


def split(s, sep=','):
    return [ss.strip() for ss in s.split(sep) if ss.strip()]


def slug(s):
    """Condensed version of s, containing only lowercase alphanumeric characters."""
    res = ''.join((c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn'))
    for c in punctuation:
        res = res.replace(c, '')
    res = re.sub('\s+', '', res)
    res = res.encode('ascii', 'ignore').decode('ascii')
    assert re.match('[ A-Za-z0-9]*$', res)
    return res


def normalize_name(s):
    """Convert a string into a valid python attribute name.

    This function is called to convert ASCII strings to something that can pass as
    python attribute name, to be used with namedtuples.
    """
    s = s.replace('-', '_').replace('.', '_').replace(' ', '_')
    if s in keyword.kwlist:
        return s + '_'
    s = '_'.join(slug(ss) for ss in s.split('_'))
    if not s:
        s = '_'
    if s[0] not in ascii_letters + '_':
        s = '_' + s
    return s


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
        n: read_tsv(data_path('conceptlists', n), unique=None)
        for n in os.listdir(data_path('conceptlists')) if not n.startswith('.')}

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
