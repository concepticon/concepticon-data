# coding:utf8
from __future__ import unicode_literals, division
from collections import Counter, defaultdict

from clldutils.badge import badge, Colors
from clldutils.path import Path
from clldutils.clilib import ParserError

from pyconcepticon.util import (
    data_path, conceptlists, rewrite, read_dicts, read_all, read_one, concept_set_meta,
)


class Linker(object):
    def __init__(self, clid):
        self.clid = clid
        self.concepts = {
            'CONCEPTICON_ID': {},  # maps ID to GLOSS
            'CONCEPTICON_GLOSS': {},  # maps GLOSS to ID
        }
        for cs in read_dicts(data_path('concepticon.tsv')):
            self.concepts['CONCEPTICON_ID'][cs['ID']] = cs['GLOSS']
            self.concepts['CONCEPTICON_GLOSS'][cs['GLOSS']] = cs['ID']

        self._cid_index = None
        self._cgloss_index = None
        self._link_col = (None, None)
        self._number_index = None

    def __call__(self, i, row):
        if i == 0:
            assert ('CONCEPTICON_ID' in row) or ('CONCEPTICON_GLOSS' in row)
            assert 'NUMBER' in row
            if ('CONCEPTICON_ID' in row) and ('CONCEPTICON_GLOSS' in row):
                self._cid_index = row.index('CONCEPTICON_ID')
                self._cgloss_index = row.index('CONCEPTICON_GLOSS')
            else:
                # either CONCEPTICON_ID or CONCEPTICON_GLOSS is given, and the other is
                # missing.
                for j, col in enumerate(row):
                    if col == 'CONCEPTICON_ID':
                        row = ['CONCEPTICON_GLOSS'] + row
                        self._link_col = (j, col)
                        break
                    if col == 'CONCEPTICON_GLOSS':
                        row = ['CONCEPTICON_ID'] + row
                        self._link_col = (j, col)
                        break
            if 'ID' not in row:
                self._number_index = row.index('NUMBER')
                row = ['ID'] + row
            return row

        if self._link_col[1]:
            val = self.concepts[self._link_col[1]].get(row[self._link_col[0]], '')
            if not val:
                print('unknown %s: %s' % (self._link_col[1], row[self._link_col[0]]))
            row = [val] + row
        else:
            cid = self.concepts['CONCEPTICON_GLOSS'].get(row[self._cgloss_index], '')
            if not cid:
                print('unknown CONCEPTICON_GLOSS: %s' % row[self._cgloss_index])
            elif cid != row[self._cid_index]:
                print('unknown CONCEPTICON_ID/GLOSS mismatch: %s %s' %
                      (row[self._cid_index], row[self._cgloss_index]))
        if self._number_index is not None:
            row = ['%s-%s' % (self.clid, row[self._number_index])] + row
        return row


def link(args):
    """\
Complete linking of concepts to concept sets. If either CONCEPTICON_GLOSS or
CONCEPTICON_ID is given, the other is added.

concepticon link <concept-list>
"""
    conceptlist = Path(args.args[0])
    if not conceptlist.exists() or not conceptlist.is_file():
        conceptlist = data_path('conceptlists', args.args[0])
        if not conceptlist.exists() or not conceptlist.is_file():
            raise ParserError('no file %s found' % args.args[0])

    rewrite(conceptlist, Linker(conceptlist.stem))


def readme(outdir, text):
    with outdir.joinpath('README.md').open('w', encoding='utf8') as fp:
        if isinstance(text, list):
            text = '\n'.join(text)
        fp.write(text)


def stats(args):
    """\
write statistics to README

concepticon stats
    """
    cls = [(cl, read_all(cl)) for cl in conceptlists()]
    readme_conceptlists(cls)
    readme_concept_list_meta()
    readme_concepticondata(cls)


def readme_conceptlists(cls):
    lines = [
        '## Concept Lists',
        '',
        ' name | mapped | mergers ',
        ' ---- | ------ | ------- ',
    ]

    for cl, concepts in cls:
        mapped = len([c for c in concepts if c.CONCEPTICON_ID])
        mapped_ratio = int((mapped / len(concepts)) * 100)
        concepticon_ids = Counter(
            [c.CONCEPTICON_ID for c in concepts if c.CONCEPTICON_ID])
        mergers = len([k for k, v in concepticon_ids.items() if v > 1])

        line = [
            '[%s](%s) ' % (cl.stem, cl.name),
            badge(
                'mapped',
                '%s%%' % mapped_ratio,
                Colors.red if mapped_ratio < 99 else Colors.brightgreen),
            badge(
                'mergers',
                '%s' % mergers,
                Colors.red if mergers else Colors.brightgreen),
        ]

        lines.append(' | '.join(line))

    readme(data_path('conceptlists'), lines)


def readme_concept_list_meta():
    """Writes statistics on metadata to readme."""
    txt = ['# Basic Statistics on Metadata\n']
    cnc = len(read_all(data_path('concepticon.tsv')))
    res = Counter([(cl.stem, len(read_all(cl))) for cl in concept_set_meta()])
    for name, n in res.most_common():
        txt.append('* {0} covers {1} concept sets ({2:.2f} %)'.format(name, n, n / cnc))
    readme(data_path('concept_set_meta'), txt)


def attributes(args):
    """Calculate the addditional attributes in the lists."""
    attrs = Counter()
    for cl in conceptlists():
        header = [
            h for h in read_one(cl)._fields if h not in [
                'ID', 'CONCEPTICON_ID', 'CONCEPTICON_GLOSS', 'ENGLISH', 'GLOSS', 'NUMBER'
            ]]
        attrs.update(header)

    txt = '# Common Additional Columns of Concept Lists\n'
    for k, v in attrs.most_common():
        txt += '* {0} {1} occurences\n'.format(k, v)
    print(txt)


def readme_concepticondata(cls):
    """
    Returns a dictionary with concept set label as value and tuples of concept
    list identifier and concept label as values.
    """
    D, G = defaultdict(list), defaultdict(list)
    labels = Counter()

    for cl, concepts in cls:
        for j, concept in enumerate(c for c in concepts if c.CONCEPTICON_ID):
            label = concept.GLOSS if hasattr(concept, 'GLOSS') else concept.ENGLISH
            D[concept.CONCEPTICON_GLOSS].append((cl.name, label))
            G[label].append((concept.CONCEPTICON_ID, concept.CONCEPTICON_GLOSS, cl.name))
            labels.update([label])

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
            sum([len(set([label for _, label in v])) for k, v in D.items()]) / len(D))
    ]

    for attr, key in [
        ('Diverse', lambda x: (len(set([label for _, label in x[1]])), x[0])),
        ('Frequent', lambda x: (len(set([clist for clist, _ in x[1]])), x[0])),
    ]:
        txt.extend([
            '# Twenty Most %s Concept Sets\n' % attr,
            '| No. | concept set | distinct labels | concept lists | examples |',
            '| --- | --- | ---:| ---:| --- |',
        ])
        for i, (k, v) in enumerate(sorted(D.items(), key=key, reverse=True)[:20]):
            txt.append('| {0} | {1} | {2} | {3} | {4} |\n'.format(
                i + 1,
                k,
                len(set([label for _, label in v])),
                len(set([clist for clist, _ in v])),
                ', '.join(sorted(set(
                    ['«{0}»'.format(label.replace('*', '`*`')) for _, label in v])))
            ))

    readme(data_path(), txt)
    return D, G
