import os
import argparse

from concepticondata.util import data_path, visit, tsv_items


class Linker(object):
    def __init__(self, clid):
        self.clid = clid
        self.concepts = {
            'CONCEPTICON_ID': {},  # maps ID to GLOSS
            'CONCEPTICON_GLOSS': {},  # maps GLOSS to ID
        }
        for cs in tsv_items(data_path('concepticon.tsv')):
            self.concepts['CONCEPTICON_ID'][cs['ID']] = cs['GLOSS']
            self.concepts['CONCEPTICON_GLOSS'][cs['GLOSS']] = cs['ID']

        self._link_col = (None, None)
        self._number_index = None

    def __call__(self, i, row):
        if i == 0:
            assert ('CONCEPTICON_ID' in row) or ('CONCEPTICON_GLOSS' in row)
            assert 'NUMBER' in row
            if ('CONCEPTICON_ID' in row) and ('CONCEPTICON_GLOSS' in row):
                pass
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
                print('missing %s: %s' % (self._link_col[1], row[self._link_col[0]]))
            row = [val] + row
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

    visit(Linker(os.path.basename(args.conceptlist).replace('.tsv', '')), args.conceptlist)
