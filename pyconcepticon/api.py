# coding: utf8
from __future__ import unicode_literals, print_function, division
import logging
from operator import itemgetter, setitem
import re
from collections import defaultdict, deque

import bibtexparser
import attr
from clldutils.path import Path
from clldutils import jsonlib
from clldutils.misc import cached_property
from clldutils.dsv import UnicodeWriter

from pyconcepticon import data
from pyconcepticon.util import (
    REPOS_PATH, PKG_PATH, data_path, read_dicts, split, lowercase, to_dict, split_ids)
from pyconcepticon.glosses import concept_map, concept_map2


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
            Conceptset(api=self, **lowercase(d))
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
        :returns: `dict` mapping concept sets to related concepts.
        """
        return ConceptRelations(self.data_path('conceptrelations.tsv'))

    @cached_property()
    def frequencies(self):
        D = defaultdict(int)
        for cl in self.conceptlists.values():
            for concept in cl.concepts.values():
                if concept.concepticon_id:
                    D[concept.concepticon_gloss] += 1
        return D

    def _metadata(self, id_):
        values_path = self.data_path('concept_set_meta', id_ + '.tsv')
        md_path = self.data_path('concept_set_meta', id_ + '.tsv-metadata.json')
        assert values_path.exists() and md_path.exists()
        return Metadata(
            id=id_,
            meta=jsonlib.load(md_path),
            values=to_dict(read_dicts(values_path), key=itemgetter('CONCEPTICON_ID')))

    def map(self, clist, otherlist=None, out=None, full_search=False,
            similarity_level=5, language='en'):
        assert clist.exists()
        from_ = []
        for item in read_dicts(clist):
            from_.append((
                item.get('ID', item.get('NUMBER')),
                item.get('GLOSS', item.get('ENGLISH'))))
        if otherlist:
            to = []
            for item in read_dicts(otherlist):
                to.append((item['ID'], item.get('GLOSS', item.get('ENGLISH'))))
        else:
            to = [
                (cs['ID'], cs['GLOSS']) for cs in read_dicts(
                    PKG_PATH.joinpath('data', 'map-{0}.tsv'.format(language)))]
        if not full_search:
            cmap = concept_map2(
                [i[1] for i in from_],
                [i[1] for i in to],
                similarity_level=similarity_level,
                freqs=self.frequencies,
                language=language)
            good_matches = 0
            with UnicodeWriter(out, delimiter='\t') as writer:
                writer.writerow([
                    'ID', 'GLOSS', 'CONCEPTICON_ID', 'CONCEPTICON_GLOSS', 'SIMILARITY'])
                for i, (fid, fgloss) in enumerate(from_):
                    row = [fid, fgloss]
                    matches, sim = cmap.get(i, ([], 10))
                    if sim <= 5:
                        good_matches += 1
                    if not matches:
                        writer.writerow(row + ['', '???', ''])
                    elif len(matches) == 1:
                        row.extend([
                            to[matches[0]][0], to[matches[0]][1].split('///')[0], sim])
                        writer.writerow(row)
                    else:
                        writer.writerow(['<<<', '', '', ''])
                        visited = set()
                        for j in matches:
                            if to[j][0] not in visited:
                                writer.writerow([
                                    fid, fgloss, to[j][0], to[j][1].split('///')[0], sim])
                                visited.add(to[j][0])
                        writer.writerow(['>>>', '', '', ''])
                writer.writerow([
                    '#',
                    good_matches,
                    len(from_),
                    '{0:.2f}'.format(good_matches / len(from_))])
        else:
            cmap = concept_map(
                [i[1] for i in from_],
                [i[1] for i in to],
                similarity_level=similarity_level)
            with UnicodeWriter(out, delimiter='\t') as writer:
                writer.writerow(['ID', 'GLOSS', 'CONCEPTICON_ID', 'CONCEPTICON_GLOSS'])
                for i, (fid, fgloss) in enumerate(from_):
                    row = [fid, fgloss]
                    match = cmap.get(i)
                    row.extend(list(to[match[0]]) if match else ['', ''])
                    writer.writerow(row)

        if out is None:
            print(writer.read().decode('utf-8'))


class Bag(object):
    @classmethod
    def public_fields(cls):
        return [f.name for f in attr.fields(cls) if not f.name.startswith('_')]


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
class Reference(Bag):
    id = attr.ib()
    type = attr.ib()
    record = attr.ib(default=attr.Factory(dict), validator=valid_bibtex_record)


@attr.s
class Conceptset(Bag):
    id = attr.ib()
    gloss = attr.ib()
    semanticfield = attr.ib(validator=valid_key)
    definition = attr.ib()
    ontological_category = attr.ib(validator=valid_key)
    _api = attr.ib(default=None)

    @cached_property()
    def relations(self):
        return self._api.relations[self.id] if self._api else {}

    @cached_property()
    def concepts(self):
        res = []
        if self._api:
            for clist in self._api.conceptlists.values():
                for concept in clist.concepts.values():
                    if concept.concepticon_id == self.id:
                        res.append(concept)
        return res


@attr.s
class Metadata(Bag):
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


_INVERSE_RELATIONS = {'broader': 'narrower'}
_INVERSE_RELATIONS.update({v: k for k, v in _INVERSE_RELATIONS.items()})


class ConceptRelations(dict):
    """
    Class handles relations between concepts.
    """
    def __init__(self, path):
        rels = defaultdict(dict)
        for item in read_dicts(path):
            rels[item['SOURCE']][item['TARGET']] = item['RELATION']
            rels[item['SOURCE_GLOSS']][item['TARGET_GLOSS']] = item['RELATION']
            if item['RELATION'] in _INVERSE_RELATIONS:
                rels[item['TARGET']][item['SOURCE']] = \
                    _INVERSE_RELATIONS[item['RELATION']]
                rels[item['TARGET_GLOSS']][item['SOURCE_GLOSS']] = \
                    _INVERSE_RELATIONS[item['RELATION']]
        dict.__init__(self, rels.items())

    def iter_related(self, concept, relation, max_degree_of_separation=2):
        """
        Search for concept relations of a given concept.

        :param search_depth: maximal depth of search
        :param relation: the concept relation to be searched (currently only
            "broader" and "narrower".

        """
        queue = deque([(concept, 0)])
        while queue:
            current_concept, depth = queue.popleft()
            depth += 1
            for target, rel in self.get(current_concept, {}).items():
                if rel == relation and depth <= max_degree_of_separation:
                    queue.append((target, depth))
                    yield (target, depth)


@attr.s
class Concept(Bag):
    id = attr.ib(validator=valid_concept)
    number = attr.ib()
    concepticon_id = attr.ib()
    concepticon_gloss = attr.ib(default=None)
    gloss = attr.ib(default=None)
    english = attr.ib(default=None)
    attributes = attr.ib(default=attr.Factory(dict))
    _list = attr.ib(default=None)

    @property
    def label(self):
        return self.gloss or self.english

    @cached_property()
    def cols(self):
        return Concept.public_fields() + list(self.attributes.keys())


@attr.s
class Conceptlist(Bag):
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
        if isinstance(self._api, Path):
            return self._api
        return self._api.data_path('conceptlists', self.id + '.tsv')

    @cached_property()
    def attributes(self):
        header = []
        if self.path.exists():
            with self.path.open(encoding='utf8') as fp:
                header = fp.readline().strip().split('\t')
        return [h for h in header if h.lower() not in Concept.public_fields()]

    @cached_property()
    def concepts(self):
        res = []
        if self.path.exists():
            for item in read_dicts(self.path):
                kw, attributes = {}, {}
                for k, v in item.items():
                    kl = k.lower()
                    setitem(kw if kl in Concept.public_fields() else attributes, kl, v)
                res.append(Concept(list=self, attributes=attributes, **kw))
        return to_dict(res)

    @classmethod
    def from_file(cls, path, **keywords):
        """
        Function loads a concept list outside the Concepticon collection.
        """
        path = Path(path)
        assert path.exists()
        attrs = {f: keywords.get(f, '') for f in Conceptlist.public_fields()}
        attrs.update(
            id=path.stem,
            items=keywords.get('items', len(read_dicts(path))),
            year=keywords.get('year', 0))
        return cls(api=path, **attrs)
