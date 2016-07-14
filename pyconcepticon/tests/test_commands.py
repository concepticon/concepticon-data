# coding: utf8
from __future__ import unicode_literals, print_function, division

from mock import Mock, patch, MagicMock
from clldutils.path import copy, Path
from clldutils.testing import WithTempDir
from clldutils.misc import nfilter

from pyconcepticon.util import read_all


class Tests(WithTempDir):
    def test_link(self):
        from pyconcepticon.commands import link

        def nattr(p, attr):
            return len(nfilter([getattr(i, attr, None) for i in read_all(p)]))

        test = self.tmp_path('test.tsv')
        copy(Path(__file__).parent.joinpath('fixtures', 'conceptlist.tsv'), test)
        self.assertEqual(nattr(test, 'CONCEPTICON_GLOSS'), 0)
        link(Mock(args=[test]))
        self.assertEqual(nattr(test, 'CONCEPTICON_GLOSS'), 1)

    def test_stats(self):
        from pyconcepticon.commands import stats

        with patch('pyconcepticon.commands.readme', Mock()) as readme:
            stats(MagicMock())
        self.assertEqual(readme.call_count, 3)
