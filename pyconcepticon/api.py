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
from clldutils.csvw.metadata import TableGroup, Link
from clldutils.apilib import API, DataObject

from pyconcepticon.util import (
    REPOS_PATH, PKG_PATH, read_dicts, split, lowercase, to_dict, split_ids, UnicodeWriter,
)
from pyconcepticon.glosses import concept_map, concept_map2


class Concepticon(API):
    """
    API to access the concepticon data.

    Objects for the various types of data stored in concepticon-data can be accessed as
    dictionaries mapping object IDs to specific object type instances.
    """
    def __init__(self, repos=None):
        """
        :param repos: Path to a clone or source dump of concepticon-data.
        """
        API.__init__(self, repos or REPOS_PATH)
        self._to_mapping = {}

    def data_path(self, *comps):
        """
        Create a path relative to the `concepticondata` directory within the source repos.
        """
        return self.path('concepticondata', *comps)

    @cached_property()
    def vocabularies(self):
        """
        Provide access to a `dict` of controlled vocabularies.
        """
        res = jsonlib.load(self.data_path('concepticon.json'))
        for k in res['COLUMN_TYPES']:
            v = res['COLUMN_TYPES'][k]
            if isinstance(v, list) and v and v[0] == 'languoid':
                res['COLUMN_TYPES'][k] = Languoid(k, *v[1:])
        return res

    @property
    def bibfile(self):
        return self.data_path('references', 'references.bib')

    @cached_property()
    def sources(self):
        return jsonlib.load(self.data_path('sources', 'cdstar.json'))

    @cached_property()
    def bibliography(self):
        """
        :returns: `dict` mapping BibTeX IDs to `Reference` instances.
        """
        log = logging.getLogger('bibtexparser')
        log.setLevel(logging.WARN)
        with self.bibfile.open(encoding='utf8') as fp:
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

    def _metadata(self, id_):
        values_path = self.data_path('concept_set_meta', id_ + '.tsv')
        md_path = self.data_path('concept_set_meta', id_ + '.tsv-metadata.json')
        assert values_path.exists() and md_path.exists()
        md = jsonlib.load(md_path)
        return Metadata(
            id=id_,
            meta=md,
            values=to_dict(
                read_dicts(values_path, schema=md['tableSchema']),
                key=itemgetter('CONCEPTICON_ID')))

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

    def _get_map_for_language(self, language, otherlist=None):
        if (language, otherlist) not in self._to_mapping:
            if otherlist is not None:
                to = []
                for item in read_dicts(otherlist):
                    to.append((item['ID'], item.get('GLOSS', item.get('ENGLISH'))))
            else:
                mapfile = PKG_PATH.joinpath('data', 'map-{0}.tsv'.format(language))
                to = [(cs['ID'], cs['GLOSS']) for cs in read_dicts(mapfile)]
            self._to_mapping[(language, otherlist)] = to
        return self._to_mapping[(language, otherlist)]

    def map(self,
            clist,
            otherlist=None,
            out=None,
            full_search=False,
            similarity_level=5,
            language='en',
            skip_multiple=False):
        assert clist.exists(), "File %s does not exist" % clist
        from_ = read_dicts(clist)

        to = self._get_map_for_language(language, otherlist)
        cmap = (concept_map if full_search else concept_map2)(
            [i.get('GLOSS', i.get('ENGLISH')) for i in from_],
            [i[1] for i in to],
            similarity_level=similarity_level,
            freqs=self.frequencies,
            language=language
        )
        good_matches = 0
        with UnicodeWriter(out) as writer:
            writer.writerow(
                list(from_[0].keys()) +
                ['CONCEPTICON_ID', 'CONCEPTICON_GLOSS', 'SIMILARITY'])
            for i, item in enumerate(from_):
                row = list(item.values())
                matches, sim = cmap.get(i, ([], 10))
                if sim <= similarity_level:
                    good_matches += 1
                if not matches:
                    writer.writerow(row + ['', '???', ''])
                elif len(matches) == 1:
                    row.extend([
                        to[matches[0]][0], to[matches[0]][1].split('///')[0], sim])
                    writer.writerow(row)
                else:
                    assert not full_search
                    # we need a list to retain the order by frequency
                    visited = []
                    for j in matches:
                        gls, cid = to[j][0], to[j][1].split('///')[0]
                        if (gls, cid) not in visited:
                            visited += [(gls, cid)]
                    if len(visited) > 1:
                        if not skip_multiple:
                            writer.writeblock(
                                row + [gls, cid, sim] for gls, cid in visited)
                    else:
                        row.extend([visited[0][0], visited[0][1], sim])
                        writer.writerow(row)
            writer.writerow(
                ['#',
                 '{0}/{1}'.format(good_matches, len(from_)),
                 '{0:.0f}%'.format(100 * good_matches / len(from_))] +
                (len(from_[0]) - 1) * [''])

        if out is None:
            print(writer.read().decode('utf-8'))

    def lookup(self, entries, full_search=False, similarity_level=5, language='en'):
        """
        :returns: `generator` of tuples (searchterm, concepticon_id, concepticon_gloss, \
        similarity).
        """
        to = self._get_map_for_language(language, None)
        cfunc = concept_map2 if full_search else concept_map
        cmap = cfunc(
            entries,
            [i[1] for i in to],
            freqs=self.frequencies,
            language=language,
            similarity_level=similarity_level)
        for i, e in enumerate(entries):
            match, simil = cmap.get(i, [[], 100])
            yield set((e, to[m][0], to[m][1].split("///")[0], simil) for m in match)


@attr.s
class Languoid(object):
    name = attr.ib(convert=lambda s: s.lower())
    glottocode = attr.ib()
    iso2 = attr.ib()


class Bag(DataObject):
    @classmethod
    def public_fields(cls):
        return [n for n in cls.fieldnames() if not n.startswith('_')]


def valid_key(instance, attribute, value):
    vocabulary = None
    if isinstance(instance._api, Concepticon):
        vocabulary = instance._api.vocabularies[attribute.name.upper()]
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
    replacement_id = attr.ib()
    _api = attr.ib(default=None)

    @property
    def superseded(self):
        return bool(self.replacement_id)

    @property
    def replacement(self):
        if self._api and self.replacement_id:
            return self._api.conceptsets[self.replacement_id]

    @cached_property()
    def relations(self):
        return self._api.relations.get(self.id, {}) if self._api else {}

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
        self.raw = list(read_dicts(path))
        for item in self.raw:
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
    concepticon_id = attr.ib(
        default=None, convert=lambda s: s if s is None else '{0}'.format(s))
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
    alias = attr.ib(convert=lambda s: [] if s is None else split(s))

    @property
    def metadata(self):
        md = self.path.parent.joinpath(self.path.name + '-metadata.json')
        if not md.exists():
            ddir = self._api.data_path() if hasattr(self._api, 'data_path') \
                else REPOS_PATH.joinpath('concepticondata')
            md = ddir.joinpath('conceptlists', 'default-metadata.json')
        tg = TableGroup.from_file(md)
        if isinstance(self._api, Path):
            tg._fname = self._api.parent.joinpath(self._api.name + '-metadata.json')
        tg.tables[0].url = Link('{0}.tsv'.format(self.id))
        return tg.tables[0]

    @property
    def path(self):
        if isinstance(self._api, Path):
            return self._api
        return self._api.data_path('conceptlists', self.id + '.tsv')

    @cached_property()
    def attributes(self):
        return [c.name for c in self.metadata.tableSchema.columns
                if c.name.lower() not in Concept.public_fields()]

    @cached_property()
    def concepts(self):
        res = []
        if self.path.exists():
            for item in self.metadata:
                kw, attributes = {}, {}
                for k, v in item.items():
                    if k:
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
