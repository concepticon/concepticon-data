# coding: utf8
from __future__ import unicode_literals, print_function, division
from collections import namedtuple

from mock import Mock, patch, MagicMock
from clldutils.path import copy
from clldutils.testing import WithTempDirMixin, capture
from clldutils.misc import nfilter
from clldutils.clilib import ParserError

from pyconcepticon.util import read_all
from pyconcepticon.tests.util import TestWithFixture


class Tests(WithTempDirMixin, TestWithFixture):
    def test_link(self):
        from pyconcepticon.commands import link

        with self.assertRaises(ParserError):
            link(Mock(args=['.'], data=None))

        def nattr(p, attr):
            return len(nfilter([getattr(i, attr, None) for i in read_all(p)]))

        test = self.tmp_path('test.tsv')
        copy(self.fixture_path('conceptlist.tsv'), test)
        self.assertEqual(nattr(test, 'CONCEPTICON_GLOSS'), 0)
        link(Mock(args=[test], data=None))
        self.assertEqual(nattr(test, 'CONCEPTICON_GLOSS'), 1)

        copy(self.fixture_path('conceptlist2.tsv'), test)
        with capture(link, Mock(args=[test], data=None)) as out:
            self.assertIn('unknown CONCEPTICON_GLOSS', out)
            self.assertIn('mismatch', out)

    def test_readme(self):
        from pyconcepticon.commands import readme

        readme(self.tmp_path(), ['a', 'b'])
        self.assertTrue(self.tmp_path('README.md').exists())

    def test_stats(self):
        from pyconcepticon.commands import stats

        with patch('pyconcepticon.commands.readme', Mock()) as readme:
            stats(MagicMock(data=None))
        self.assertEqual(readme.call_count, 3)

    def test_attributes(self):
        from pyconcepticon.commands import attributes

        with capture(attributes, MagicMock(data=None)) as out:
            self.assertIn('Occurrences', out)

    def test_union(self):
        from pyconcepticon.commands import union
        Args = namedtuple('Args', ['data', 'args'])

        with capture(
                union,
                Args(data='', args=['Swadesh-1955-100', 'Swadesh-1952-200'])) as out:
            self.assertEqual(208, len(out.split('\n')))

        with capture(
                union,
                Args(data='', args=['Swadesh-1952-200', 'Matisoff-1978-200'])) as out:
            self.assertEqual(301, len(out.split('\n')))

    def test_intersection(self):
        from pyconcepticon.commands import intersection
        Args = namedtuple('Args', ['data', 'args'])

        with capture(
                intersection,
                Args(data='', args=['Swadesh-1955-100', 'Swadesh-1952-200'])) as out:
            self.assertEqual(94, len(out.split('\n')))

    def test_lookup(self):
        from pyconcepticon.commands import lookup
        with capture(
                lookup, MagicMock(full_search=True, args=['sky'], language='en')) as out:
            self.assertIn('1732', out)
        with capture(lookup, MagicMock(args=['sky'], language='en')) as out:
            self.assertIn('1732', out)
