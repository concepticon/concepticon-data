from __future__ import unicode_literals
import re
import warnings
from collections import namedtuple

from clldutils.jsonlib import load
from clldutils.misc import normalize_name
from clld.lib.bibtex import Database

from pyconcepticon import data
from pyconcepticon.util import (
    data_path, read_dicts, split_ids, conceptlists, concept_set_meta,
)


SUCCESS = True
NUMBER_PATTERN = re.compile('(?P<number>[0-9]+)(?P<suffix>.*)')


def split(s, sep=','):
    return [ss.strip() for ss in s.split(sep) if ss.strip()]


def error(msg, name, line=''):  # pragma: no cover
    global SUCCESS
    SUCCESS = False
    if line:
        line = ':%s' % line
    print('ERROR:%s%s: %s' % (name, line, msg))


def warning(msg, name, line=''):  # pragma: no cover
    if line:
        line = ':%s' % line
    warnings.warn('WARNING:%s%s: %s' % (name, line, msg), Warning)


def read_tsv(path, unique='ID'):
    uniquevalues = set()
    rows = []
    for line, row in enumerate(read_dicts(path)):
        line += 2
        if None in row:
            error('too many columns', path, line)  # pragma: no cover
        if unique:
            if unique not in row:  # pragma: no cover
                error('unique key missing: %s' % unique, path, line)
                continue
            if row[unique] in uniquevalues:  # pragma: no cover
                error('non-unique %s: %s' % (unique, row[unique]), path, line)
            uniquevalues.add(row[unique])
        rows.append((line, row))
    return rows


def test():
    if not data_path().exists():
        return  # pragma: no cover

    # load bibtex
    bib = Database.from_file(data_path('references', 'references.bib'))
    assert bib

    cls = {
        cl.name: read_tsv(cl, unique=None)
        for cl in conceptlists() if not cl.stem.startswith('.')}

    read_tsv(data_path('concepticon.tsv'))
    concepticon = read_tsv(data_path('concepticon.tsv'), unique='GLOSS')

    for i, cs in concepticon:
        for attr in ['SEMANTICFIELD', 'ONTOLOGICAL_CATEGORY']:
            valid = getattr(data, attr)
            value = cs[attr]
            if value and value not in valid:  # pragma: no cover
                error('invalid %s: %s' % (attr, value), data_path('concepticon.tsv'), i)

    # We collect all cite keys used to refer to references.
    all_refs = set()
    for source in concept_set_meta():
        specs = load(source.parent.joinpath(source.stem + '.tsv-metadata.json'))
        tsv = read_tsv(source, unique='CONCEPTICON_ID')
        cnames = [var['name'] for var in specs['tableSchema']['columns']]
        if not [n for n in cnames if n in list(tsv[0][1])]:  # pragma: no cover
            error('column names in {0} but not in json-specs'.format(source.stem), 'name')
        for i, line in tsv:
            if len(line) != len(cnames):  # pragma: no cover
                error('meta data {0} contains irregular number of columns in line {1}'
                      .format(source.stem, i), 'name')
        if 'dc:references' in specs:
            all_refs.add(specs['dc:references'])

    # Make sure only records in the BibTeX file references.bib are referenced by
    # concept lists.
    clmd = data_path('conceptlists.tsv')
    clids = {}
    visited1, visited2 = set(), set()
    tags = getattr(data, 'CL_TYPES')

    for i, cl in read_tsv(clmd):
        clids[cl['ID']] = cl
        for ref in split_ids(cl['REFS']):
            if ref not in bib.keymap and ref not in visited1:  # pragma: no cover
                error('unknown bibtex record "%s" referenced' % ref, clmd, i)
                visited1.add(ref)
            else:  # pragma: no cover
                # we fail when author/editor, or year, or title/booktitle are missing
                if 'Title' not in bib[ref] \
                        and 'Booktitle' not in bib[ref] \
                        and ref not in visited2:
                    error('missing bibtex title in record "%s"' % ref, clmd, i)
                    visited2.add(ref)
                if 'Author' not in bib[ref] and 'Editor' not in bib[ref]:
                    error('missing bibtex author/editor in record "%s"' % ref, clmd, i)
                    visited2.add(ref)
                if 'Year' not in bib[ref]:
                    error('missing bibtex year in record "%s"' % ref, clmd, i)
                    visited2.add(ref)
            all_refs.add(ref)

        for tag in split_ids(cl['TAGS']):
            if tag not in tags:  # pragma: no cover
                error('invalid cl type: %s' % tag, clmd, i)

    for i, ref in enumerate(bib.keymap):
        if ref not in all_refs:  # pragma: no cover
            error('bibtex record %s is in the references but not referenced in the data.'
                  % ref, clmd, i)

    #
    # make also sure that all sources are accompanied as pdf, but only write a
    # warning if this is not the case
    #
    pdfs = [f.stem for f in data_path('sources').glob('*.pdf')]
    no_pdf_for_source = set()
    for i, cl in read_tsv(clmd):
        for ref in split_ids(cl['PDF']):
            if ref not in pdfs:  # pragma: no cover
                no_pdf_for_source.add(ref)
    
    if no_pdf_for_source:  # pragma: no cover
        warning(
            '\n'.join(no_pdf_for_source),
            'no pdf found for {0} sources'.format(len(no_pdf_for_source)))
    
    ref_cols = {
        'CONCEPTICON_ID': set(cs[1]['ID'] for cs in concepticon),
        'CONCEPTICON_GLOSS': set(cs[1]['GLOSS'] for cs in concepticon),
    }

    for name, concepts in cls.items():
        try:
            cl = clids[name.replace('.tsv', '')]
        except KeyError:  # pragma: no cover
            error('unkown record {0} referenced'.format(name), '', '')
            cl = {}

        missing = []
        for i, (line, concept) in enumerate(concepts):
            if i == 0:  # pragma: no cover
                cols = list(concept.keys())
                try:
                    namedtuple('nt', [normalize_name(n) for n in cols])
                except ValueError as e:
                    error('%s' % e, name, line)
                for lg in split(cl.get('SOURCE_LANGUAGE', '')):
                    if lg.upper() not in cols:
                        error('missing source language col %s' % lg.upper(), name, '')

            for lg in split(cl.get('SOURCE_LANGUAGE', '')):
                if not concept.get(lg.upper()):  # pragma: no cover
                    error('missing source language translation %s' % lg.upper(), name, line)
            if not NUMBER_PATTERN.match(concept['NUMBER']):  # pragma: no cover
                error('invalid concept NUMBER %(NUMBER)s' % concept, name, line)
            for col, values in ref_cols.items():
                if col not in concept:
                    if col not in missing:  # pragma: no cover
                        error('missing column %s' % col, name)
                        missing.append(col)
                elif concept[col] and concept[col] not in values:  # pragma: no cover
                    error('invalid value for %s: %s' % (col, concept[col]), name, line)

    if not SUCCESS:  # pragma: no cover
        raise ValueError('integrity checks failed!')
