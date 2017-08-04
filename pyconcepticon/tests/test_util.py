# coding: utf8
from __future__ import unicode_literals, print_function, division

from cdstarcat.catalog import Object, Bitstream
from clldutils.testing import WithTempDir
from clldutils.jsonlib import load
from clldutils.path import read_text


class Tests(WithTempDir):
    def test_UnicodeWriter(self):
        from pyconcepticon.util import UnicodeWriter

        with UnicodeWriter(self.tmp_path('tst')) as fp:
            with self.assertRaises(AssertionError):
                fp.writeblock([['a', 'b'], ['c', 'd']])
            fp.writerow(['x', 'y'])
            fp.writeblock([['a', 'b'], ['c', 'd']])
        self.assertEqual(
            read_text(self.tmp_path('tst')), 'x\ty\n#<<<\t\na\tb\nc\td\n#>>>\t\n')

    def test_to_dict(self):
        from pyconcepticon.util import to_dict

        with self.assertRaises(ValueError):
            to_dict([None, None], id)

    def test_load_conceptlist(self):
        from pyconcepticon.util import load_conceptlist, write_conceptlist, visit

        fname = self.tmp_path('cl.tsv')
        with fname.open('w', encoding='utf8') as fp:
            fp.write("""\
ID	NUMBER	ENGLISH	PROTOWORLD	CONCEPTICON_ID	CONCEPTICON_GLOSS
Bengtson-1994-27-1	1	mother, older femaile relative	AJA	1216	MOTHER
Bengtson-1994-27-1	2	knee, to bend	BU(N)KA	1371
""")

        res = load_conceptlist(fname)
        assert res['splits']
        out = self.tmp_path('clist')
        write_conceptlist(res, out)
        assert out.exists()

        visit(lambda l, r: r, fname)

    def test_SourcesCatalog(self):
        from pyconcepticon.util import SourcesCatalog

        cat_path = self.tmp_path('test.json')
        with SourcesCatalog(cat_path) as cat:
            cat.add(
                'key', Object('id', [Bitstream('bsid', 5, 'text/plain', '', '', '')], {}))
            self.assertIn('key', cat)
            self.assertIn('url', cat.get('key'))

        self.assertIn('key', load(cat_path))

    def test_natural_sort(self):
        from pyconcepticon.util import natural_sort

        source = ['Elm11', 'Elm12', 'Elm2', 'elm0', 'elm1', 'elm10', 'elm13', 'elm9']
        target = ['elm0', 'elm1', 'Elm2', 'elm9', 'elm10', 'Elm11', 'Elm12', 'elm13']
        self.assertEqual(natural_sort(source), target)
