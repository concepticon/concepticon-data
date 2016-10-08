# coding: utf8
from __future__ import unicode_literals, print_function, division
import logging
from operator import itemgetter, setitem
import re
from collections import defaultdict

import bibtexparser
import attr
from clldutils.path import Path
from clldutils import jsonlib
from clldutils.misc import cached_property
from clldutils.dsv import UnicodeWriter, UnicodeReader

from pyconcepticon import data
from pyconcepticon.util import (
    REPOS_PATH, data_path, read_dicts, split, lowercase, to_dict, split_ids,
)
from pyconcepticon.glosses import concept_map


class Concepticon(object):
    """
    API to access the concepticon data.

    Objects for the various types of data stored in concepticon-data can be accessed as
    dictionaries mapping object IDs to specific object type instances.
    """
    def __init__(self, repos=None):
        """
        :param repos: Path to a clone or source dump of concepticon-data.
        """
        self.repos = Path(repos) if repos else REPOS_PATH

    def data_path(self, *comps):
        """
        Create a path relative to the `concepticondata` directory within the source repos.
        """
        return data_path(*comps, **{'repos': self.repos})

    @cached_property()
    def bibliography(self):
        """
        :returns: `dict` mapping BibTeX IDs to `Reference` instances.
        """
        log = logging.getLogger('bibtexparser')
        log.setLevel(logging.WARN)
        with self.data_path('references', 'references.bib').open(encoding='utf8') as fp:
            refs = []
            for rec in bibtexparser.loads(fp.read()).entries:
                refs.append(
                    Reference(id=rec.pop('ID'), type=rec.pop('ENTRYTYPE'), record=rec))
        return to_dict(refs)

    @cached_property()
    def conceptsets(self):
        """
        :returns: `dict` mapping ConceptSet IDs to `Conceptset` instances.
        """
        return to_dict(
            Conceptset(**lowercase(d))
            for d in read_dicts(self.data_path('concepticon.tsv')))

    @cached_property()
    def conceptlists(self):
        """
        :returns: `dict` mapping ConceptList IDs to `Conceptlist` instances.

        .. note:: Individual concepts can be accessed via `Conceptlist.concepts`.
        """
        return to_dict(
            Conceptlist(api=self, **lowercase(d))
            for d in read_dicts(self.data_path('conceptlists.tsv')))

    @cached_property()
    def metadata(self):
        """
        :returns: `dict` mapping metadata provider IDs to `Metadata` instances.
        """
        return to_dict(map(
            self._metadata,
            [p.stem for p in self.data_path('concept_set_meta').glob('*.tsv')]))

    @cached_property()
    def relations(self):
        """
        :returns: `dict` mapping concepts to parent or child concepts.
        """
        return ConceptRelations(self.data_path('conceptrelations.tsv'))

    def _metadata(self, id_):
        values_path = self.data_path('concept_set_meta', id_ + '.tsv')
        md_path = self.data_path('concept_set_meta', id_ + '.tsv-metadata.json')
        assert values_path.exists() and md_path.exists()
        return Metadata(
            id=id_,
            meta=jsonlib.load(md_path),
            values=to_dict(read_dicts(values_path), key=itemgetter('CONCEPTICON_ID')))

    def map(self, clist, out=None):
        assert clist.exists()
        from_ = []
        for item in read_dicts(clist):
            from_.append((item['ID'], item.get('GLOSS', item.get('ENGLISH'))))
        to = [(cs.id, cs.gloss) for cs in self.conceptsets.values()]
        cmap = concept_map([i[1] for i in from_], [i[1] for i in to])

        with UnicodeWriter(out, delimiter='\t') as writer:
            writer.writerow(['ID', 'GLOSS', 'CONCEPTICON_ID', 'CONCEPTICON_GLOSS'])
            for i, (fid, fgloss) in enumerate(from_):
                row = [fid, fgloss]
                match = cmap.get(i)
                row.extend(list(to[match[0]]) if match else ['', ''])
                writer.writerow(row)

        if out is None:
            print(writer.read().decode('utf-8'))


def valid_key(instance, attribute, value):
    vocabulary = getattr(data, attribute.name.upper(), None)
    if value and vocabulary:
        if not isinstance(value, (list, tuple)):
            value = [value]
        if not all(v in vocabulary for v in value):
            raise ValueError('invalid {0}.{1}: {2}'.format(
                instance.__class__.__name__,
                attribute.name,
                value))


def valid_bibtex_record(instance, attribute, value):
    for req in [['title', 'booktitle'], ['author', 'editor'], ['year']]:
        if not any(key in value for key in req):
            raise ValueError('missing any of %s in record %s' % (req, instance.id))


@attr.s
class Reference(object):
    id = attr.ib()
    type = attr.ib()
    record = attr.ib(default=attr.Factory(dict), validator=valid_bibtex_record)


@attr.s
class Conceptset(object):
    id = attr.ib()
    gloss = attr.ib()
    semanticfield = attr.ib(validator=valid_key)
    definition = attr.ib()
    ontological_category = attr.ib(validator=valid_key)


@attr.s
class Metadata(object):
    id = attr.ib()
    meta = attr.ib(default=attr.Factory(dict))
    values = attr.ib(default=attr.Factory(dict))


def valid_concept(instance, attribute, value):
    if not value:
        raise ValueError('missing concept id %s' % instance)
    if not re.match('[0-9]+.*', instance.number):
        raise ValueError('invalid concept number: %s' % instance)
    if not instance.label:
        raise ValueError('fields gloss *and* english missing: %s' % instance)

class ConceptRelations(dict):
    """
    Class handles relations between concepts.
    """
    def __init__(self, path):
        rels = defaultdict(dict)
        with UnicodeReader(path, delimiter='\t') as reader:
            data = list(reader)
        for srci, srcg, rel, tari, targ in data[1:]:
            if rel == 'narrower':
                rels[srci][tari] = rel
                rels[tari][srci] = 'broader'
                rels[srcg][targ] = rel
                rels[targ][srcg] = 'broader'
            elif rel == 'broader':
                rels[srci][tari] = rel
                rels[tari][srci] = 'narrower'
                rels[srcg][targ] = rel
                rels[targ][srcg] = 'narrower'
        dict.__init__(self, rels.items())

    def walk(self, concept, relation, search_depth=2):
        """
        Search for concept relations of a given concept.

        :param search_depth: maximal depth of search
        :param relation: the concept relation to be searched (currently only
            "broader" and "narrower".

        """
        queue = [(concept, 0)]
        while queue:
            current_concept, depth = queue.pop(0)
            depth += 1
            for c, r in self.get(current_concept, {}).items():
                if r == relation and depth <= search_depth:
                    queue += [(c, depth)]
                    yield (c, depth)

    def broader(self, concept, searchdepth=2):
        """Search for all concepts which are related as "broader"."""
        return self.walk(concept, 'broader', searchdepth)

    def narrower(self, concept, searchdepth=2):
        """Search for all concepts which are related as "narrower"."""
        return self.walk(concept, 'narrower')


@attr.s
class Concept(object):
    id = attr.ib(validator=valid_concept)
    number = attr.ib()
    concepticon_id = attr.ib()
    concepticon_gloss = attr.ib()
    gloss = attr.ib(default=None)
    english = attr.ib(default=None)
    attributes = attr.ib(default=attr.Factory(dict))

    @property
    def label(self):
        return self.gloss or self.english

    @cached_property()
    def cols(self):
        return [f.name for f in attr.fields(self.__class__)] \
               + list(self.attributes.keys())


@attr.s
class Conceptlist(object):
    _api = attr.ib()
    id = attr.ib()
    author = attr.ib()
    year = attr.ib(convert=int)
    list_suffix = attr.ib()
    items = attr.ib(convert=int)
    tags = attr.ib(convert=split_ids, validator=valid_key)
    source_language = attr.ib(convert=lambda v: split(v.lower()))
    target_language = attr.ib()
    url = attr.ib()
    refs = attr.ib(convert=split_ids)
    pdf = attr.ib(convert=split_ids)
    note = attr.ib()
    pages = attr.ib()
    alias = attr.ib(convert=split)

    @property
    def path(self):
        return self._api.data_path('conceptlists', self.id + '.tsv')

    @cached_property()
    def attributes(self):
        header = []
        if self.path.exists():
            with self.path.open(encoding='utf8') as fp:
                header = fp.readline().strip().split('\t')
        standard_cols = [f.name for f in attr.fields(Concept)]
        return [h for h in header if h.lower() not in standard_cols]

    @cached_property()
    def concepts(self):
        standard_cols = [f.name for f in attr.fields(Concept)]
        res = []
        if self.path.exists():
            for item in read_dicts(self.path):
                kw, attributes = {}, {}
                for k, v in item.items():
                    kl = k.lower()
                    setitem(kw if kl in standard_cols else attributes, kl, v)
                res.append(Concept(attributes=attributes, **kw))
        return to_dict(res)
