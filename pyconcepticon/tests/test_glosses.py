# coding: utf8
from __future__ import unicode_literals, print_function, division
from unittest import TestCase


class Tests(TestCase):
    def test_parse_gloss(self):
        from pyconcepticon.glosses import parse_gloss, Gloss

        for g, res in [
            (
                'the dog (n)',
                ('dog', '(', 'n', ')', 'noun', '', 'dog', 'the dog (n)')),
            (
                'to be a dog',
                ('a dog', '', '', '', 'verb', 'be', 'dog', 'to be a dog')),
            (
                "to kill",
                ('kill', '', '', '', 'verb', '', 'kill', 'to kill')),
            (
                "kill",
                ('kill', '', '', '', '', '', 'kill', 'kill')),
            (
                "kill (v.)",
                ('kill', '(', 'v.', ')', 'verb', '', 'kill', 'kill (v.)')),
            (
                "kill (somebody)",
                ('kill', '(', 'somebody', ')', '', '', 'kill', 'kill (somebody)')),
        ]:
            self.assertEqual(parse_gloss(g)[0], Gloss(*res))

        self.assertEqual(parse_gloss('the mountain or hill')[1].pos, 'noun')

        g = Gloss.from_string('the mountain or hill')
        self.assertEqual(g.tokens, 'the mountain hill')

        g1 = Gloss.from_string('der Berg', language='de')
        g2 = Gloss.from_string('Berg')
        self.assertEqual(g1.similarity(g2), 4)

        g = Gloss.from_string('la montagne', language='fr')
        self.assertEqual(g.pos, '')

        g1 = Gloss.from_string('montagne', language='fr')
        g2 = Gloss.from_string('la montagne', language='fr')
        self.assertEqual(g1.similarity(g2), 6)

        # error on invalid gloss
        with self.assertRaises(ValueError):
            parse_gloss(None)

    def test_concept_map(self):
        from pyconcepticon.glosses import concept_map

        f, t = ['the dog', 'to kill'], ['kill', 'dog (verb)', 'to kill']
        self.assertEqual(concept_map(f, t), {0: ([1], 4), 1: ([2], 1)})
        self.assertNotIn(0, concept_map(f, t, similarity_level=1))
