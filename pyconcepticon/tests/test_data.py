from __future__ import unicode_literals
import re
import warnings

from pyconcepticon.api import Concepticon
from pyconcepticon.util import split, REPOS_PATH


SUCCESS = True
NUMBER_PATTERN = re.compile('(?P<number>[0-9]+)(?P<suffix>.*)')


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


def test():
    if not REPOS_PATH.exists():
        return  # pragma: no cover

    api = Concepticon(REPOS_PATH)

    # We collect all cite keys used to refer to references.
    all_refs = set()
    for meta in api.metadata.values():
        cnames_schema = set(var['name'] for var in meta.meta['tableSchema']['columns'])
        cnames_tsv = set(list(meta.values.values())[0])
        if cnames_tsv - cnames_schema:  # pragma: no cover
            error('column names in {0} but not in json-specs'.format(meta.id), 'name')
        for i, value in enumerate(meta.values.values()):
            if set(value.keys()) != cnames_schema:  # pragma: no cover
                error('meta data {0} contains irregular number of columns in line {1}'
                      .format(meta.id, i + 2), 'name')
        for ref in split(meta.meta.get('dc:references', '')):
            all_refs.add(ref)

    # Make sure only records in the BibTeX file references.bib are referenced by
    # concept lists.
    clmd = api.data_path('conceptlists.tsv')

    for i, cl in enumerate(api.conceptlists.values()):
        for ref in cl.refs:
            if ref not in api.bibliography:  # pragma: no cover
                error('unknown bibtex record "%s" referenced' % ref, clmd, i + 2)
            all_refs.add(ref)

    for ref in api.bibliography:
        if ref not in all_refs:  # pragma: no cover
            error('bibtex record %s is in the references but not referenced in the data.'
                  % ref, clmd, 0)

    #
    # make also sure that all sources are accompanied as pdf, but only write a
    # warning if this is not the case
    #
    pdfs = [f.stem for f in api.data_path('sources').glob('*.pdf')]
    no_pdf_for_source = set()
    for cl in api.conceptlists.values():
        for ref in cl.pdf:
            if ref not in pdfs:  # pragma: no cover
                no_pdf_for_source.add(ref)

    if no_pdf_for_source:  # pragma: no cover
        warning(
            '\n'.join(no_pdf_for_source),
            'no pdf found for {0} sources'.format(len(no_pdf_for_source)))

    ref_cols = {
        'concepticon_id': set(api.conceptsets.keys()),
        'concepticon_gloss': set(cs.gloss for cs in api.conceptsets.values()),
    }

    for fname in api.data_path('conceptlists').glob('*.tsv'):
        if fname.stem not in api.conceptlists:  # pragma: no cover
            error(
                'conceptlist missing in conceptlists.tsv: {0}'.format(fname.name), '', '')

    for cl in api.conceptlists.values():
        for i, concept in enumerate(cl.concepts.values()):
            if i == 0:  # pragma: no cover
                for lg in cl.source_language:
                    if lg.lower() not in concept.cols:
                        error('missing source language col %s' % lg.upper(), cl.id, '')

            for lg in cl.source_language:  # pragma: no cover
                if not (concept.attributes.get(lg.lower()) or getattr(concept, lg.lower(), None)):
                    error('missing source language translation %s' % lg, cl.id, i + 2)
            for attr, values in ref_cols.items():
                val = getattr(concept, attr)
                if val and val not in values:  # pragma: no cover
                    error('invalid value for %s: %s' % (attr, val), cl.id, i + 2)

    if not SUCCESS:  # pragma: no cover
        raise ValueError('integrity checks failed!')
