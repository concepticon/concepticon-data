# coding: utf8
from __future__ import unicode_literals, print_function, division

import pytest
from cdstarcat.catalog import Object, Bitstream
from clldutils.jsonlib import load

from pyconcepticon.util import *


def test_UnicodeWriter(tmpdir):
    tst = tmpdir.join('tst')
    with UnicodeWriter(str(tst)) as fp:
        with pytest.raises(AssertionError):
            fp.writeblock([['a', 'b'], ['c', 'd']])
        fp.writerow(['x', 'y'])
        fp.writeblock([['a', 'b'], ['c', 'd']])
    assert tst.read_text('utf8') == "x\ty\n#<<<\t\na\tb\nc\td\n#>>>\t\n"


def test_to_dict():
    with pytest.raises(ValueError):
        to_dict([None, None], id)


def test_load_conceptlist(tmpdir):
    fname = tmpdir.join('cl.tsv')
    fname.write("""\
ID	NUMBER	ENGLISH	PROTOWORLD	CONCEPTICON_ID	CONCEPTICON_GLOSS
Bengtson-1994-27-1	1	mother, older femaile relative	AJA	1216	MOTHER
Bengtson-1994-27-1	2	knee, to bend	BU(N)KA	1371
""")

    res = load_conceptlist(str(fname))
    assert res['splits']
    out = tmpdir.join('clist')
    write_conceptlist(res, str(out))
    assert out.read_text('utf8')
    visit(lambda l, r: r, str(fname))


def test_SourcesCatalog(tmpdir):
    cat_path = tmpdir.join('test.json')
    with SourcesCatalog(str(cat_path)) as cat:
        cat.add(
            'key', Object('id', [Bitstream('bsid', 5, 'text/plain', '', '', '')], {}))
        assert 'key' in cat
        assert 'url' in cat.get('key')

    assert 'key' in load(str(cat_path))


def test_natural_sort():
    source = ['Elm11', 'Elm12', 'Elm2', 'elm0', 'elm1', 'elm10', 'elm13', 'elm9']
    target = ['elm0', 'elm1', 'Elm2', 'elm9', 'elm10', 'Elm11', 'Elm12', 'elm13']
    assert natural_sort(source) == target
