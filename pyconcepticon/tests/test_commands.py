# coding: utf8
from __future__ import unicode_literals, print_function, division

from mock import Mock, patch, MagicMock
from clldutils.path import copy, Path
from clldutils.testing import WithTempDir, capture
from clldutils.misc import nfilter
from clldutils.clilib import ParserError

from pyconcepticon.util import read_all


class Tests(WithTempDir):
    def test_link(self):
        from pyconcepticon.commands import link

        with self.assertRaises(ParserError):
            link(Mock(args=['.']))

        def nattr(p, attr):
            return len(nfilter([getattr(i, attr, None) for i in read_all(p)]))

        test = self.tmp_path('test.tsv')
        copy(Path(__file__).parent.joinpath('fixtures', 'conceptlist.tsv'), test)
        self.assertEqual(nattr(test, 'CONCEPTICON_GLOSS'), 0)
        link(Mock(args=[test]))
        self.assertEqual(nattr(test, 'CONCEPTICON_GLOSS'), 1)

    def test_readme(self):
        from pyconcepticon.commands import readme

        readme(self.tmp_path(), ['a', 'b'])
        self.assertTrue(self.tmp_path('README.md').exists())

    def test_stats(self):
        from pyconcepticon.commands import stats

        with patch('pyconcepticon.commands.readme', Mock()) as readme:
            stats(MagicMock())
        self.assertEqual(readme.call_count, 3)

    def test_attributes(self):
        from pyconcepticon.commands import attributes

        with capture(attributes, MagicMock()) as out:
            self.assertIn('Columns', out)
