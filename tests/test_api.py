# coding: utf8
from __future__ import unicode_literals, print_function, division

import pytest
from pyconcepticon.api import Concepticon


@pytest.fixture(scope='module')
def api():
    return Concepticon()


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


def test_Conceptlist(fixturedir):
    from pyconcepticon.api import Conceptlist

    clist = Conceptlist.from_file(fixturedir.joinpath('conceptlist.tsv'))
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
        assert len(api.editors) == 4


def test_map(api, capsys, fixturedir):
    if api.repos.exists():
        api.map(fixturedir.joinpath('conceptlist.tsv'))
        out, err = capsys.readouterr()
        assert 'CONCEPTICON_ID' in out
        assert len(api.conceptsets['217'].concepts) > 8

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
    assert len(api.frequencies) <= len(api.conceptsets)


def test_ConceptRelations(fixturedir):
    from pyconcepticon.api import ConceptRelations
    rels = ConceptRelations(fixturedir.joinpath('conceptrelations.tsv'))
    assert list(rels.iter_related('1212', 'narrower'))[0][0] == '1131'
    assert list(rels.iter_related('1212', 'hasform'))[0][0] == '2310'

def test_superseded_concepts(api):
    # 282 POLE has a replacement to 281 POST
    assert api.conceptsets['282'].superseded
    assert api.conceptsets['282'].replacement == api.conceptsets['281']
    