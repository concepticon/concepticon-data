# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.testing import capture

from pyconcepticon.api import Concepticon
from pyconcepticon.tests.util import TestWithFixture


class Tests(TestWithFixture):
    def test_Concept(self):
        from pyconcepticon.api import Concept

        d = {f: '' for f in Concept.public_fields()}
        with self.assertRaises(ValueError):
            Concept(**d)

        d['id'] = 'i'
        with self.assertRaises(ValueError):
            Concept(**d)

        d['number'] = 'i'
        with self.assertRaises(ValueError):
            Concept(**d)

        d['number'] = '1b'
        with self.assertRaises(ValueError):
            Concept(**d)

        d['gloss'] = 'g'
        Concept(**d)

    def test_Conceptlist(self):
        from pyconcepticon.api import Conceptlist

        clist = Conceptlist.from_file(self.fixture_path('conceptlist.tsv'))
        self.assertEqual(len(clist.concepts), 1)

    def test_Reference(self):
        from pyconcepticon.api import Reference

        with self.assertRaises(ValueError):
            Reference(id=1, type='misc', record={})

        Reference(id=1, type='misc', record={'author': 'a', 'title': 't', 'year': 'y'})


class TestConcepticon(TestWithFixture):
    @classmethod
    def setupClass(cls):
        cls.api = Concepticon()

    def test_Conceptset(self):
        from pyconcepticon.api import Conceptset

        d = {a: '' for a in Conceptset.public_fields()}
        d['semanticfield'] = 'xx'
        d['api'] = self.api
        with self.assertRaises(ValueError):
            Conceptset(**d)

    def test_map(self):
        if self.api.repos.exists():
            with capture(self.api.map, self.fixture_path('conceptlist.tsv')) as out:
                self.assertIn('CONCEPTICON_ID', out)

            self.assertGreater(len(self.api.conceptsets['217'].concepts), 8)

            with capture(
                    self.api.map,
                    self.fixture_path('conceptlist.tsv'),
                    self.fixture_path('conceptlist2.tsv')) as out:
                self.assertIn('CONCEPTICON_ID', out)

    def test_lookup(self):
        if self.api.repos.exists():
            self.assertEqual(
                list(self.api.lookup(['sky', 'sun'])),
                [
                    {('sky', '1732', 'SKY', 2)},
                    {('sun', '1343', 'SUN', 2)},
                ])
            # there are at least five 'thins' so lets see if we get them.
            assert len(list(self.api.lookup(['thin'], full_search=True))[0]) >= 5

    def test_Concepticon(self):
        assert len(self.api.frequencies) <= len(self.api.conceptsets)
