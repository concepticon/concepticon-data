# coding: utf8
from __future__ import unicode_literals, print_function, division
from unittest import TestCase

import attr


class Tests(TestCase):
    def test_Concept(self):
        from pyconcepticon.api import Concept

        d = {a.name: '' for a in attr.fields(Concept)}
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

    def test_Conceptset(self):
        from pyconcepticon.api import Conceptset

        d = {a.name: '' for a in attr.fields(Conceptset)}
        d['semanticfield'] = 'xx'
        with self.assertRaises(ValueError):
            Conceptset(**d)

    def test_Reference(self):
        from pyconcepticon.api import Reference

        with self.assertRaises(ValueError):
            Reference(id=1, type='misc', record={})

        Reference(id=1, type='misc', record={'author': 'a', 'title': 't', 'year': 'y'})
