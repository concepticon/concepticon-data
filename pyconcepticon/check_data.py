# coding: utf8
from __future__ import unicode_literals
import re
import warnings

from pyconcepticon.api import Concepticon, CONCEPTLIST_ID_PATTERN, REF_PATTERN
from pyconcepticon.util import split, REPOS_PATH, BIB_PATTERN


SUCCESS = True
NUMBER_PATTERN = re.compile('(?P<number>[0-9]+)(?P<suffix>.*)')


def _msg(type_, msg, name, line):  # pragma: no cover
    if line:
        line = ':%s' % line
    return '%s:%s%s: %s' % (type_.upper(), name, line or '', msg)


def error(msg, name, line=0):  # pragma: no cover
    global SUCCESS
    SUCCESS = False
    print(_msg('error', msg, name, line))


def warning(msg, name, line=0):  # pragma: no cover
    warnings.warn(_msg('warning', msg, name, line), Warning)


def check(api=None):
    if not api:
        if not REPOS_PATH.exists():
            return  # pragma: no cover
        api = Concepticon(REPOS_PATH)

    # We collect all cite keys used to refer to references.
    all_refs = set()
    refs_in_bib = set(ref for ref in api.bibliography)
    for meta in api.metadata.values():
        cnames_schema = set(var['name'] for var in meta.meta['tableSchema']['columns'])
        cnames_tsv = set(list(meta.values.values())[0])
        if cnames_tsv - cnames_schema:  # pragma: no cover
            error('column names in {0} but not in json-specs'.format(meta.id), 'name')
        for i, value in enumerate(meta.values.values()):
            if set(value.keys()) != cnames_schema:  # pragma: no cover
                error('meta data {0} contains irregular number of columns in line {1}'
                      .format(meta.id, i + 2), 'name')
        for ref in split(meta.meta.get('dc:references') or ''):
            if ref not in refs_in_bib:
                error('cited bibtex record not in bib: {0}'.format(ref), 'name')
            all_refs.add(ref)

    # Make sure only records in the BibTeX file references.bib are referenced by
    # concept lists.
    for i, cl in enumerate(api.conceptlists.values()):
        for ref in re.findall(BIB_PATTERN, cl.note) + cl.refs:
            if ref not in refs_in_bib:
                error('cited bibtex record not in bib: {0}'.format(ref), 'conceptlists.tsv', i + 2)
            else:
                all_refs.add(ref)

        for m in REF_PATTERN.finditer(cl.note):
            if m.group('id') not in api.conceptlists:
                error('invalid conceptlist ref: {0}'.format(m.group('id')), 'conceptlists.tsv', i + 2)

        # make also sure that all sources are accompanied by a PDF, but only write a
        # warning if this is not the case
        for ref in cl.pdf:
            if ref not in api.sources:  # pragma: no cover
                warning('no PDF found for {0}'.format(ref), 'conceptlists.tsv')
    all_refs.add('List2016a')

    for ref in refs_in_bib - all_refs:
        error('unused bibtex record: {0}'.format(ref), 'references.bib')

    ref_cols = {
        'concepticon_id': set(api.conceptsets.keys()),
        'concepticon_gloss': set(cs.gloss for cs in api.conceptsets.values()),
    }

    for i, rel in enumerate(api.relations.raw):
        for attr, type_ in [
            ('SOURCE', 'concepticon_id'),
            ('TARGET', 'concepticon_id'),
            ('SOURCE_GLOSS', 'concepticon_gloss'),
            ('TARGET_GLOSS', 'concepticon_gloss'),
        ]:
            if rel[attr] not in ref_cols[type_]:  # pragma: no cover
                error(
                    'invalid {0}: {1}'.format(attr, rel[attr]), 'conceptrelations', i + 2)

    for fname in api.data_path('conceptlists').glob('*.tsv'):
        if fname.stem not in api.conceptlists:  # pragma: no cover
            error(
                'conceptlist missing in conceptlists.tsv: {0}'.format(fname.name), '')

    for cl in api.conceptlists.values():
        for i, concept in enumerate(cl.concepts.values()):
            if i == 0:  # pragma: no cover
                for lg in cl.source_language:
                    if lg.lower() not in concept.cols:
                        error('missing source language col %s' % lg.upper(), cl.id)

            for lg in cl.source_language:  # pragma: no cover
                if not (concept.attributes.get(lg.lower()) or
                        getattr(concept, lg.lower(), None) or
                        (lg.lower() == 'english' and not concept.gloss)):
                    error('missing source language translation %s' % lg, cl.id, i + 2)
            for attr, values in ref_cols.items():
                val = getattr(concept, attr)
                if val:
                    # check that there are not leading and trailing spaces
                    # (while computationally expensive, this helps catch really
                    # hard to find typos)
                    if val != val.strip():
                        error("leading or trailing spaces in value for %s: '%s'" %
                              (attr, val), cl.id, i + 2)

                    if val not in values:  # pragma: no cover
                        error('invalid value for %s: %s' % (attr, val), cl.id, i + 2)

    sameas = {}
    glosses = set()
    for cs in api.conceptsets.values():
        if cs.gloss in glosses:  # pragma: no cover
            error('duplicate conceptset gloss: {0}'.format(cs.gloss), cs.id)
        glosses.add(cs.gloss)
        for target, rel in cs.relations.items():
            if rel == 'sameas':
                for group in sameas.values():
                    if target in group:  # pragma: no cover
                        group.add(cs.id)
                        break
                else:
                    sameas[cs.gloss] = {cs.id, target}

    deprecated = {}
    for s in sameas.values():
        csids = sorted(s, key=lambda j: int(j))
        for csid in csids[1:]:
            assert csid not in deprecated
            deprecated[csid] = csids[0]

    for cl in api.conceptlists.values():
        for concept in cl.concepts.values():
            if concept.concepticon_id in deprecated:  # pragma: no cover
                error('deprecated concept set {0} linked for {1}'.format(
                    concept.concepticon_id, concept.id), cl.id)

    return SUCCESS
