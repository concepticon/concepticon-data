# coding: utf8
from __future__ import unicode_literals, print_function, division

import pytest


def test_Concept():
    from pyconcepticon.api import Concept

    d = {f: '' for f in Concept.public_fields()}
    with pytest.raises(ValueError):
        Concept(**d)

    d['id'] = 'i'
    with pytest.raises(ValueError):
        Concept(**d)

    d['number'] = 'i'
    with pytest.raises(ValueError):
        Concept(**d)

    d['number'] = '1b'
    with pytest.raises(ValueError):
        Concept(**d)

    d['gloss'] = 'g'
    Concept(**d)


def test_Conceptlist(fixturedir, api, mocker):
    from pyconcepticon.api import Conceptlist

    mocker.patch('pyconcepticon.api.REPOS_PATH', fixturedir)
    clist = Conceptlist.from_file(fixturedir.joinpath('conceptlist.tsv'), api=api)
    assert len(clist.concepts) == 1


def test_Reference():
    from pyconcepticon.api import Reference

    with pytest.raises(ValueError):
        Reference(id=1, type='misc', record={})

    Reference(id=1, type='misc', record={'author': 'a', 'title': 't', 'year': 'y'})


def test_Conceptset(api):
    from pyconcepticon.api import Conceptset

    d = {a: '' for a in Conceptset.public_fields()}
    d['semanticfield'] = 'xx'
    d['api'] = api
    with pytest.raises(ValueError):
        Conceptset(**d)


def test_editors(api):
    if api.repos.exists():
        assert len(api.editors) == 1


def test_map(api, capsys, fixturedir):
    api.map(fixturedir.joinpath('conceptlist.tsv'))
    out, err = capsys.readouterr()
    assert 'CONCEPTICON_ID' in out
    assert len(api.conceptsets['1'].concepts) == 0

    api.map(
        fixturedir.joinpath('conceptlist.tsv'),
        fixturedir.joinpath('conceptlist2.tsv'))
    out, err = capsys.readouterr()
    assert 'CONCEPTICON_ID' in out


def test_lookup(api):
    if api.repos.exists():
        assert list(api.lookup(['sky', 'sun'])) == \
            [
                {('sky', '1732', 'SKY', 2)},
                {('sun', '1343', 'SUN', 2)},
            ]
        # there are at least four 'thins' so lets see if we get them.
        assert len(list(api.lookup(['thin'], full_search=True))[0]) >= 4


def test_Concepticon(api):
    assert len(api.frequencies) == 941
    assert len(api.conceptsets) == 3175


def test_ConceptRelations(fixturedir):
    from pyconcepticon.api import ConceptRelations
    rels = ConceptRelations(fixturedir / 'concepticondata' / 'conceptrelations.tsv')
    assert list(rels.iter_related('1212', 'narrower'))[0][0] in ['1130', '1131']
    assert list(rels.iter_related('1212', 'hasform'))[0][0] == '2310'


def test_superseded_concepts(api):
    # 282 POLE has a replacement to 281 POST
    assert api.conceptsets['283'].superseded
    assert api.conceptsets['283'].replacement == api.conceptsets['140']
