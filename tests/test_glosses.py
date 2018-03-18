# coding: utf8
from __future__ import unicode_literals, print_function, division

import pytest

from pyconcepticon.glosses import *


def test_parse_gloss():
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
        assert parse_gloss(g)[0] == Gloss(*res)

    assert parse_gloss('the mountain or hill')[1].pos == 'noun'

    g = Gloss.from_string('the mountain or hill')
    assert g.tokens == 'the mountain hill'

    g1 = Gloss.from_string('der Berg', language='de')
    g2 = Gloss.from_string('Berg')
    assert g1.similarity(g2) == 4

    g = Gloss.from_string('la montagne', language='fr')
    assert g.pos == ''

    g1 = Gloss.from_string('montagne', language='fr')
    g2 = Gloss.from_string('la montagne', language='fr')
    assert g1.similarity(g2) == 6

    # error on invalid gloss
    with pytest.raises(ValueError):
        parse_gloss(None)

    with pytest.raises(ValueError):
        parse_gloss('')


def test_concept_map():
    f, t = ['the dog', 'to kill'], ['kill', 'dog (verb)', 'to kill']
    assert concept_map(f, t) == {0: ([1], 4), 1: ([2], 1)}
    assert 0 not in concept_map(f, t, similarity_level=1)
