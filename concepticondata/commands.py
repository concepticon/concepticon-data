# coding:utf8
from __future__ import unicode_literals, division
import os
import argparse
from collections import Counter

from clldutils.dsv import reader, rewrite
from clldutils.badge import badge, Colors
from clldutils.path import Path

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

def metadata(write_stats=True):
    """Writes statistics on metadata to readme."""
    txt = '# Basic Statistics on Metadata\n\n'
    cnc = list(reader(data_path('concepticon.tsv'), namedtuples=True, delimiter="\t"))
    for i,cl in enumerate(PKG_PATH.joinpath('concept_set_meta').glob('*.tsv')):
        data = list(reader(cl, namedtuples=True, delimiter="\t"))
        txt += '* {0} covers {1} concept sets ({2:.2f} %)\n'.format(cl.name[:-4], len(data), len(data) / len(cnc))
    if write_stats:
        with PKG_PATH.joinpath('concept_set_meta', 'README.md').open('w', encoding='utf8') as fp:
            fp.write(txt)

def list_attributes(write_stats=True):
    """Calculate the addditional attributes in the lists."""
    D = {}
    for i,cl in enumerate(PKG_PATH.joinpath('conceptlists').glob('*.tsv')):
        header = list(reader(cl, delimiter="\t"))[0]
        header = [h for h in header if h not in ['ID', 'CONCEPTICON_ID', 
            'CONCEPTICON_GLOSS', 'ENGLISH', 'GLOSS', 'NUMBER']]
        for h in header:
            try:
                D[h] += [cl.name]
            except KeyError:
                D[h] = [cl.name]
    txt = '# Common Additional Columns of Concept Lists\n'
    for k,v in sorted(D.items(), key=lambda x: len(x[1]), reverse=True):
        txt += '* {2} occurences: {0}, {1}\n'.format(k, ', '.join(v), len(v))
    print(txt)

def reflexes(write_stats=True, path='concepticondata'):
    """
    Returns a dictionary with concept set label as value and tuples of concept
    list identifier and concept label as values.
    """
    D, G = {}, {}
    cpl = 0
    cln = 0
    clb = set([])
    
    dpath = Path(path) if path else PKG_PATH
    
    for i, cl in enumerate(dpath.joinpath('conceptlists').glob('*.tsv')):
        concepts = list(reader(cl, namedtuples=True, delimiter="\t"))
        for j,concept in enumerate([c for c in concepts if c.CONCEPTICON_ID]):
            label = concept.GLOSS if hasattr(concept, 'GLOSS') else concept.ENGLISH
            name = cl.name
            try:
                D[concept.CONCEPTICON_GLOSS] += [(name, label)]
            except KeyError:
                D[concept.CONCEPTICON_GLOSS] = [(name, label)]
            try:
                G[label] += [(concept.CONCEPTICON_ID, concept.CONCEPTICON_GLOSS, name)]
            except KeyError:
                G[label] = [(concept.CONCEPTICON_ID, concept.CONCEPTICON_GLOSS, name)]
            clb.add(label)
            cpl += 1
        cln += 1
    # write basic statistics and most frequent glosses
    if write_stats:
        txt = """# Concepticon Statistics
* concept sets (used): {0}
* concept lists: {1}
* concept labels: {2}
* concept labels (unique): {3}
* Ø concepts per list: {4:.2f}
* Ø concepts per concept set: {5:.2f}
* Ø unique concept labels per concept set: {6:.2f}

"""
        txt = txt.format(
            len(D),
            cln,
            cpl,
            len(clb),
            cpl / cln,
            sum([len(v) for k,v in D.items()]) / len(D),
            sum([len(set([label for _,label in v])) for k,v in D.items()]) / len(D)
            )
        
        txt += '# Twenty Most Diverse Concept Sets\n\n'
        txt += '| No. | concept set | distinct labels | concept lists | examples |\n'
        txt += '| --- | --- | --- | --- | --- |\n'
        for i,(k,v) in enumerate(sorted(D.items(), key=lambda x: len(set([label for _,label in
            x[1]])), reverse=True)[:20]):
            txt += '| {0} | {1} | {2} | {3} | {4} |\n'.format(
                    i+1,
                    k,
                    len(set([label for _,label in v])),
                    len(set([clist for clist,_ in v])),
                    ', '.join(sorted(set(['«{0}»'.format(label.replace('*','`*`')) for _,label in
                        v])))
                    )

        txt += '# Twenty Most Frequent Concept Sets\n\n'
        txt += '| No. | concept set | distinct labels | concept lists | examples |\n'
        txt += '| --- | --- | --- | --- | --- |\n'
        for i,(k,v) in enumerate(sorted(D.items(), key=lambda x: len(set([clist for clist,_ in
            x[1]])), reverse=True)[:20]):
            txt += '| {0} | {1} | {2} | {3} | {4} |\n'.format(
                    i+1,
                    k,
                    len(set([label for _,label in v])),
                    len(set([clist for clist,_ in v])),
                    ', '.join(sorted(set(['«{0}»'.format(label.replace('*','`*`')) for _,label in
                        v])))
                    )

        with dpath.joinpath('README.md').open('w', encoding='utf8') as fp:
            fp.write(txt)

    return D, G


