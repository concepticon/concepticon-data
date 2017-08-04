# coding:utf8
from __future__ import unicode_literals, division
import os
from collections import Counter, defaultdict
import operator
from functools import partial

from six import text_type
from tabulate import tabulate
from clldutils.path import Path, as_unicode
from clldutils.clilib import ParserError, command
from clldutils.markup import Table
from clldutils.misc import format_size
from cdstarcat.catalog import Catalog

import pyconcepticon
from pyconcepticon.util import rewrite, CS_ID, CS_GLOSS, SourcesCatalog, UnicodeWriter
from pyconcepticon.api import Concepticon, Conceptlist


class Linker(object):
    def __init__(self, clid, conceptsets):
        self.clid = clid
        self.concepts = {
            CS_ID: {cs.id: cs.gloss for cs in conceptsets},
            # maps ID to GLOSS
            CS_GLOSS: {cs.gloss: cs.id for cs in conceptsets},
            # maps GLOSS to ID
        }

        self._cid_index = None
        self._cgloss_index = None
        self._link_col = (None, None)
        self._number_index = None

    def __call__(self, i, row):
        if i == 0:
            assert (CS_ID in row) or (CS_GLOSS in row)
            assert 'NUMBER' in row
            if (CS_ID in row) and (CS_GLOSS in row):
                self._cid_index = row.index(CS_ID)
                self._cgloss_index = row.index(CS_GLOSS)
            else:
                # either CONCEPTICON_ID or CONCEPTICON_GLOSS is given, and the
                # other is missing.
                add = {
                    CS_ID: CS_GLOSS,
                    CS_GLOSS: CS_ID}
                for j, col in enumerate(row):
                    if col in add:
                        row = [add[col]] + row
                        self._link_col = (j, col)
                        break
            if 'ID' not in row:
                self._number_index = row.index('NUMBER')
                row = ['ID'] + row
            return row

        if self._link_col[1]:
            val = self.concepts[self._link_col[1]].get(row[self._link_col[0]], '')
            if not val:
                print('unknown %s: %s' % (
                    self._link_col[1],
                    row[self._link_col[0]]))
            row = [val] + row
        else:
            cid = self.concepts[CS_GLOSS].get(row[self._cgloss_index], '')
            if not cid:
                print('unknown CONCEPTICON_GLOSS: {0}'.format(
                    row[self._cgloss_index]))
            elif cid != row[self._cid_index]:
                if not row[self._cid_index]:
                    row[self._cid_index] = cid
                else:
                    print('unknown CONCEPTICON_ID/GLOSS mismatch: %s %s' % (
                        row[self._cid_index], row[self._cgloss_index]))

        if self._number_index is not None:
            row = ['%s-%s' % (self.clid, row[self._number_index])] + row
        return row


@command()
def link(args):
    """
    Complete linking of concepts to concept sets. If either CONCEPTICON_GLOSS or
    CONCEPTICON_ID is given, the other is added.

    concepticon link <concept-list>
    """
    api = Concepticon(args.data)
    conceptlist = Path(args.args[0])
    if not conceptlist.exists() or not conceptlist.is_file():
        conceptlist = api.data_path('conceptlists', args.args[0])
        if not conceptlist.exists() or not conceptlist.is_file():
            raise ParserError('no file %s found' % args.args[0])

    rewrite(conceptlist, Linker(conceptlist.stem, api.conceptsets.values()))


@command()
def validate(args):
    api = Concepticon(args.data)
    for cl in api.conceptlists.values():
        items = list(cl.metadata)
        if set(items[0].keys()) != \
                set(c.name for c in cl.metadata.tableSchema.columns):
            print('unspecified column in concept list {0}'.format(cl.id))


@command()
def attributes(args):
    """Calculate the addditional attributes in the lists."""
    api = Concepticon(args.data)
    attrs = Counter()
    for cl in api.conceptlists.values():
        attrs.update(cl.attributes)

    print(tabulate(list(attrs.most_common()), headers=(
        'Attribute', 'Occurrences')))


def compare_conceptlists(api, *conceptlists, **kw):
    """
    Function compares multiple conceptlists and extracts common concepts.

    Note
    ----
    The method takes concept relations into account.
    """
    search_depth = kw.pop('search_depth', 3)
    commons = defaultdict(set)

    # store all concepts along with their broader concepts
    for arg in conceptlists:
        if arg not in api.conceptlists:
            clist = Conceptlist.from_file(arg)
        else:
            clist = api.conceptlists[arg]
        for c in clist.concepts.values():
            if c.concepticon_id:
                commons[c.concepticon_id].add((
                    arg, 0, c.concepticon_id, c.concepticon_gloss))
                for rel, depth in [
                    ('broader', partial(operator.add, 0)),
                    ('narrower', partial(operator.sub, 0))
                ]:
                    for cn, d in api.relations.iter_related(
                            c.concepticon_id, rel, max_degree_of_separation=search_depth):
                        commons[cn].add((
                            arg, depth(d), c.concepticon_id, c.concepticon_gloss))

    # store proper concepts (the ones purely underived), as we need to check in
    # a second run, whether a narrower concept occurs (don't find another
    # solution for this)
    proper_concepts = set()
    for c, lists in commons.items():
        if len(set([x[0] for x in lists])) > 1 and [d for l, d, i, g in lists if d == 0]:
            proper_concepts.add(c)

    # get a list of concepts that should be split into subsets (so they should
    # not be retained, such as arm/hand if arm and hand occur in certain lists
    # the blacklist is needed to make sure that narrower concepts which are
    # combined by adding a broader concept are not added additionally
    split_concepts = set([])
    blacklist = set([])
    for cid, lists in commons.items():
        if len(lists) > 1:
            # if one list makes MORE distinctions than the other, yield the
            # more refined list
            listcheck = defaultdict(list)
            for a, b, c, d in lists:
                if b >= 0:
                    listcheck[a] += [(a, b, c, d)]
            for l, concepts in listcheck.items():
                if len([x for x in concepts if x[1] > 0]) > 1:
                    split_concepts.add(cid)
                    break
            if cid not in split_concepts:
                if len([l for l in lists if l[1] > 0]) == len(lists):
                    if len(set([l[2] for l in lists])) > 1:
                        for l in lists:
                            blacklist.add(l[2])

    for cid, lists in sorted(
            commons.items(), key=lambda x: api.conceptsets[x[0]].gloss):
        sorted_lists = sorted(lists)
        depths = [x[1] for x in sorted_lists]
        reflexes = [x[2] for x in sorted_lists]

        if cid not in split_concepts:
            # yield unique concepts directly
            if len(lists) == 1:
                if next(iter(lists))[1] == 0 and cid not in blacklist:
                    yield (cid, lists)
            # check broader or narrower concept collections
            elif 0 not in depths:
                concepts = dict([(c, (a, b)) for a, b, c, d in sorted_lists])
                # if all concepts are narrower, dont' retain them
                retain = bool([x for x in depths if x > 0])
                for concept in concepts:
                    if concept in proper_concepts:
                        retain = False
                        break
                if retain:
                    yield (cid, lists)
            else:
                # if one list makes MORE distinctions than the other, yield the
                # more refined list
                if [x for x in depths if x < 0]:
                    dont_yield = False
                    for d, c in zip(depths, reflexes):
                        if d < 0 and c not in split_concepts:
                            dont_yield = True
                    if not dont_yield:
                        yield (cid, lists)
                else:
                    yield (cid, lists)


def _set_operation(args, type_):
    assert type_ in ['union', 'intersection']
    api = Concepticon(args.data)
    out, clen = [], 0

    for c, lists in compare_conceptlists(api, *args.args):
        if type_ == 'union' \
                or len(set([x[0] for x in lists if x[1] >= 0])) == len(args.args):
            marker = '*' if not len([0 for x in lists if x[1] == 0]) else ' '
            marker += '<' if len([x for x in lists]) < len(args.args) else ' '
            out += [(
                marker, c,
                api.conceptsets[c].gloss, ', '.join(
                    ['{0[3]} ({0[1]}, {0[0]})'.format(x) for x in
                     lists if x[1] != 0]))]
            clen = len(out[-1][2]) if len(out[-1][2]) > clen else clen

    frmt = '{0:3} {1:1}{2:' + text_type(clen) + '} [{3:4}] {4}'
    for i, line in enumerate(out):
        print(frmt.format(i + 1, line[0], line[2], line[1], line[3]))
    return out


@command()
def intersection(args):
    """
    Compare how many concepts overlap in concept lists.

    Note
    ----
    This takes concept relations into account by searching for each concept
    set for broader concept sets in the depth of two edges on the network. If
    one concept A in one list is broader than concept B in another list, the
    concept A will be retained, and this will be marked in output. If two lists
    share the same broader concept, they will also be retained, but only, if
    none of the narrower concepts match. As a default we use a depth of 2 for
    the search.
    """
    return _set_operation(args, 'intersection')


@command()
def union(args):
    """Calculate the union of several concept lists."""
    return _set_operation(args, 'union')


@command()
def map_concepts(args):
    api = Concepticon(args.data)
    api.map(
        Path(args.args[0]),
        otherlist=args.args[1] if len(args.args) > 1 else None,
        out=args.output,
        full_search=args.full_search,
        language=args.language,
        skip_multiple=args.skip_multimatch)


def readme(outdir, text):
    with outdir.joinpath('README.md').open('w', encoding='utf8') as fp:
        if isinstance(text, list):
            text = '\n'.join(text)
        fp.write(text)


@command()
def stats(args):
    """
    write statistics to README

    concepticon stats
    """
    api = Concepticon(args.data)
    cls = api.conceptlists.values()
    readme_conceptlists(api, cls)
    readme_concept_list_meta(api)
    readme_concepticondata(api, cls)


def readme_conceptlists(api, cls):
    table = Table('name', '# mapped', '% mapped', 'mergers')
    for cl in cls:
        concepts = cl.concepts.values()
        mapped = len([c for c in concepts if c.concepticon_id])
        mapped_ratio = 0
        if concepts:
            mapped_ratio = int((mapped / len(concepts)) * 100)
        concepticon_ids = Counter(
            [c.concepticon_id for c in concepts if c.concepticon_id])
        mergers = len([k for k, v in concepticon_ids.items() if v > 1])
        table.append(['[%s](%s) ' % (cl.id, cl.path.name), mapped, mapped_ratio, mergers])
    readme(
        api.data_path('conceptlists'),
        '# Concept Lists\n\n{0}'.format(
            table.render(verbose=True, sortkey=operator.itemgetter(0))))


def readme_concept_list_meta(api):
    """Writes statistics on metadata to readme."""
    txt = '# Basic Statistics on Metadata\n\n{0}'
    cnc = len(api.conceptsets)
    table = Table('provider', 'ID', '# concept sets', '% coverage')
    for meta in api.metadata.values():
        n = len(meta.values)
        table.append([meta.meta.get('dc:title'), meta.id, n, (n / cnc) * 100])
    readme(
        api.data_path('concept_set_meta'),
        txt.format(
            table.render(
                sortkey=operator.itemgetter(1),
                reverse=True,
                condensed=False)))


def readme_concepticondata(api, cls):
    """
    Returns a dictionary with concept set label as value and tuples of concept
    list identifier and concept label as values.
    """
    D, G = defaultdict(list), defaultdict(list)
    labels = Counter()

    for cl in cls:
        for concept in [c for c in cl.concepts.values() if c.concepticon_id]:
            D[concept.concepticon_gloss].append(
                (cl.id, concept.label))
            G[concept.label].append(
                (concept.concepticon_id, concept.concepticon_gloss, cl.id))
            labels.update([concept.label])

    txt = [
        """
# Concepticon Statistics
* concept sets (used): {0}
* concept lists: {1}
* concept labels: {2}
* concept labels (unique): {3}
* Ø concepts per list: {4:.2f}
* Ø concepts per concept set: {5:.2f}
* Ø unique concept labels per concept set: {6:.2f}

""".format(
            len(D),
            len(cls),
            sum(list(labels.values())),
            len(labels),
            sum(list(labels.values())) / len(cls),
            sum([len(v) for k, v in D.items()]) / len(D),
            sum([len(set([label for _, label in v])) for k, v in D.items()]) /
            len(D))
    ]

    for attr, key in [
        ('Diverse', lambda x: (len(set([label for _, label in x[1]])), x[0] or '')),
        ('Frequent', lambda x: (len(set([clist for clist, _ in x[1]])), x[0] or '18G18G')),
    ]:
        table = Table(
            'No.', 'concept set', 'distinct labels', 'concept lists', 'examples')
        for i, (k, v) in enumerate(
                sorted(D.items(), key=key, reverse=True)[:20]):
            table.append([
                i + 1,
                k,
                len(set([label for _, label in v])),
                len(set([clist for clist, _ in v])),
                ', '.join(sorted(set(
                    ['«{0}»'.format(
                        label.replace('*', '`*`')) for _, label in v])))
            ])
        txt.append('## Twenty Most {0} Concept Sets\n\n{1}\n'.format(
            attr, table.render()))

    readme(api.data_path(), txt)
    return D, G


@command()
def upload_sources(args):
    """
    concepticon upload_sources path/to/cdstar/catalog
    """
    catalog_path = args.args[0] if args.args else os.environ['CDSTAR_CATALOG']
    toc = ['# Sources\n']
    api = Concepticon(args.data)
    with SourcesCatalog(api.data_path('sources', 'cdstar.json')) as lcat:
        with Catalog(
                catalog_path,
                cdstar_url=os.environ['CDSTAR_URL'],
                cdstar_user=os.environ['CDSTAR_USER'],
                cdstar_pwd=os.environ['CDSTAR_PWD']) as cat:
            for fname in sorted(
                    api.data_path('sources').glob('*.pdf'), key=lambda f: f.stem):
                clid = as_unicode(fname.stem)
                spec = lcat.get(clid)
                if not spec:
                    _, _, obj = list(cat.create(fname, {'collection': 'concepticon'}))[0]
                    spec = lcat.add(clid, obj)

        for key in sorted(lcat.items):
            spec = lcat.get(key)
            toc.append('- [{0} [PDF {1}]]({2})'.format(
                key, format_size(spec['size']), spec['url']))

    readme(api.data_path('sources'), toc)
    print(catalog_path)


@command()
def lookup(args):
    """
    Looks up a single gloss from the commandline.

    concepticon lookup <gloss1 gloss2 ... glossN>
    """
    api = Concepticon()
    found = api.lookup(
        args.args,
        language=args.language,
        full_search=args.full_search,
        similarity_level=args.similarity)
    with UnicodeWriter(None) as writer:
        writer.writerow(['GLOSS', 'CONCEPTICON_ID', 'CONCEPTICON_GLOSS', 'SIMILARITY'])
        for matches in found:
            for m in matches:
                writer.writerow(m)
        print(writer.read().decode('utf-8'))


@command()
def check(args):
    """
    Identifies some issues with concept lists.
    -- i.e. multiple words with the same CONCEPTICON_ID or missing definitions

    concepticon check [CONCEPTLIST_ID]+
    """
    def _pprint(clist, error, _id, message):
        print("\t".join([
            clist.ljust(30), error.ljust(10), '%5s' % _id, message]))

    def _get_mergers(o, api):
        clashes = defaultdict(list)
        for cid, c in o.concepts.items():
            if c.concepticon_id != '':
                clashes[c.concepticon_id].append(cid)

        for c in sorted([c for c in clashes if len(clashes[c]) > 1]):
            matches = [m for m in o.concepts if o.concepts[m].concepticon_id == c]
            for i, m in enumerate(matches, 1):
                message = '#%d %s = "%s"' % (
                    i,
                    api.conceptsets[c].gloss,
                    getattr(o.concepts[m], 'english', '')
                )
                _pprint(o.id, 'MERGE', c, message)

    def _get_missing(o, _):
        for m in o.concepts:
            if o.concepts[m].concepticon_id == "":
                _pprint(
                    o.id, 'MISSING', o.concepts[m].number, '"%s"' % o.concepts[m].english)

    api = Concepticon(args.data)
    for clist in api.conceptlists:
        if (len(args.args) and clist in args.args) or not args.args:
            clist = api.conceptlists[clist]
            _get_missing(clist, api)
            _get_mergers(clist, api)


@command()
def test(args):
    from pyconcepticon.tests.test_data import test as _test
    _test()


@command()
def recreate_linking_data(args):
    api = Concepticon(args.data)
    for l in api.vocabularies['COLUMN_TYPES'].values():
        if getattr(l, 'iso2', None):
            _write_linking_data(api, l)


def _write_linking_data(api, l):
    out = defaultdict(int)
    freqs = defaultdict(int)

    for clist in api.conceptlists.values():
        for row in clist.concepts.values():
            if row.concepticon_id:
                gls = None
                if l.iso2 == 'en':
                    if row.english:
                        gls = row.english.strip('*$-—+')
                else:
                    if l.name in row.attributes:
                        gls = row.attributes[l.name].strip('*$-—+')

                if gls:
                    out[row.concepticon_gloss + '///' + gls, row.concepticon_id] += 1
                    freqs[row.concepticon_id] += 1

    if l.iso2 == 'en':
        for cset in api.conceptsets.values():
            gloss = cset.gloss
            if cset.ontological_category == 'Person/Thing':
                out[gloss + '///the ' + cset.gloss.lower(), cset.id] = freqs[cset.id]
                out[gloss + '///the ' + cset.gloss.lower() + 's', cset.id] = \
                    freqs[cset.id]
            elif cset.ontological_category == 'Action/Process':
                out[gloss + '///to ' + cset.gloss.lower(), cset.id] = freqs[cset.id]
            elif cset.ontological_category == 'Property':
                out[gloss + '///' + cset.gloss.lower() + ' (adjective)', cset.id] = \
                    freqs[cset.id]
            elif cset.ontological_category == 'Classifier':
                out[gloss + '///' + cset.gloss.lower() + ' (classifier)', cset.id] = \
                    freqs[cset.id]
            else:
                out[gloss + '///' + cset.gloss.lower(), cset.id] = freqs[cset.id]

    p = Path(pyconcepticon.__file__).parent.joinpath('data', 'map-{0}.tsv'.format(l.iso2))
    with UnicodeWriter(p, delimiter='\t') as f:
        f.writerow(['ID', 'GLOSS', 'PRIORITY'])
        for i, (gloss, cid) in enumerate(sorted(out)):
            f.writerow([cid, gloss, out[gloss, cid]])
