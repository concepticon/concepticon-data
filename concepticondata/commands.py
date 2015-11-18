from __future__ import unicode_literals, division
import os
import argparse
from collections import Counter

from clldutils.dsv import reader, rewrite
from clldutils.badge import badge, Colors

from concepticondata.util import data_path, PKG_PATH


class Linker(object):
    def __init__(self, clid):
        self.clid = clid
        self.concepts = {
            'CONCEPTICON_ID': {},  # maps ID to GLOSS
            'CONCEPTICON_GLOSS': {},  # maps GLOSS to ID
        }
        for cs in reader(data_path('concepticon.tsv'), dicts=True, delimiter='\t'):
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


def link():
    parser = argparse.ArgumentParser(
        description="""\
Complete linking of concepts to concept sets. If either CONCEPTICON_GLOSS or
CONCEPTICON_ID is given, the other is added.""")
    parser.add_argument('conceptlist', help='path to conceptlist to complete')
    args = parser.parse_args()

    if not os.path.exists(args.conceptlist):
        args.conceptlist = data_path('conceptlists', args.conceptlist)
        assert os.path.exists(args.conceptlist)

    rewrite(
        args.conceptlist,
        Linker(os.path.basename(args.conceptlist).replace('.tsv', '')),
        delimiter='\t')


def stats():
    lines = [
        '## Concept Lists',
        '',
        ' name | mapped | mergers ',
        ' ---- | ------ | ------- ',
    ]

    for cl in sorted(
            PKG_PATH.joinpath('conceptlists').glob('*.tsv'), key=lambda _cl: _cl.name):
        concepts = list(reader(cl, namedtuples=True, delimiter='\t'))
        mapped = len([c for c in concepts if c.CONCEPTICON_ID])
        mapped_ratio = int((mapped / len(concepts)) * 100)
        concepticon_ids = Counter(
            [c.CONCEPTICON_ID for c in concepts if c.CONCEPTICON_ID])
        mergers = len([k for k, v in concepticon_ids.items() if v > 1])

        line = [
            '[%s](%s) ' % (cl.stem, cl.name),
            badge('mapped', '%s%%' % mapped_ratio, Colors.red if mapped_ratio < 99 else Colors.brightgreen),
            badge('mergers', '%s' % mergers, Colors.red if mergers else Colors.brightgreen),
        ]

        lines.append(' | '.join(line))

    with PKG_PATH.joinpath('conceptlists', 'README.md').open('w', encoding='utf8') as fp:
        fp.write('\n'.join(lines))
