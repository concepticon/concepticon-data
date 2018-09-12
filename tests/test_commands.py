# coding: utf8
from __future__ import unicode_literals, print_function, division
from collections import namedtuple

import pytest
from clldutils.path import copy, Path
from clldutils.misc import nfilter
from clldutils.clilib import ParserError

from pyconcepticon.util import read_all
from pyconcepticon import __main__


def test_validate(fixturedir, mocker, capsys):
    from pyconcepticon.commands import validate
    validate(mocker.MagicMock(repos=fixturedir))
    out, err = capsys.readouterr()
    assert 'unspecified column' in out


def test_check_new(fixturedir, capsys, mocker, tmpdir):
    from pyconcepticon.commands import check_new

    test = tmpdir.join('test.tsv')
    copy(fixturedir.joinpath('conceptlist2.tsv'), str(test))
    check_new(mocker.Mock(args=[str(test)], repos=fixturedir))
    out, err = capsys.readouterr()
    assert 'Gloss DUST' in out


def test_link(mocker, fixturedir, tmpdir, capsys):
    from pyconcepticon.commands import link

    with pytest.raises(ParserError):
        link(mocker.Mock(args=['.'], repos=None))

    def nattr(p, attr):
        return len(nfilter([getattr(i, attr, None) for i in read_all(str(p))]))

    test = tmpdir.join('test.tsv')
    copy(fixturedir.joinpath('conceptlist.tsv'), str(test))
    assert nattr(test, 'CONCEPTICON_GLOSS') == 0
    link(mocker.Mock(args=[str(test)], repos=fixturedir))
    assert nattr(test, 'CONCEPTICON_GLOSS') == 1

    copy(fixturedir.joinpath('conceptlist2.tsv'), str(test))
    link(mocker.Mock(args=[str(test)], repos=fixturedir))
    out, err = capsys.readouterr()
    assert 'unknown CONCEPTICON_GLOSS' in out
    assert 'mismatch' in out


def test_readme(tmpdir):
    from pyconcepticon.commands import readme

    readme(Path(str(tmpdir)), ['a', 'b'])
    assert tmpdir.join('README.md').ensure()


def test_stats(mocker, fixturedir):
    from pyconcepticon.commands import stats

    readme = mocker.Mock()
    mocker.patch('pyconcepticon.commands.readme', readme)
    stats(mocker.MagicMock(repos=fixturedir))
    assert readme.call_count == 3


def test_attributes(mocker, capsys, fixturedir):
    from pyconcepticon.commands import attributes

    attributes(mocker.MagicMock(repos=fixturedir))
    out, err = capsys.readouterr()
    assert 'Occurrences' in out


def test_union(capsys, fixturedir):
    from pyconcepticon.commands import union
    Args = namedtuple('Args', ['repos', 'args'])

    union(Args(repos=fixturedir, args=['Perrin-2010-110', 'Sun-1991-1004']))
    out, err = capsys.readouterr()
    assert 920 == len(out.split('\n'))


def test_intersection(capsys, fixturedir):
    from pyconcepticon.commands import intersection
    Args = namedtuple('Args', ['repos', 'args'])

    intersection(Args(repos=fixturedir, args=['Perrin-2010-110', 'Sun-1991-1004']))
    out, err = capsys.readouterr()
    assert 69 == len(out.split('\n'))


def test_lookup(capsys, mocker):
    from pyconcepticon.commands import lookup

    lookup(mocker.MagicMock(full_search=True, args=['sky'], language='en'))
    out, err = capsys.readouterr()
    assert '1732' in out

    lookup(mocker.MagicMock(args=['sky'], language='en'))
    out, err = capsys.readouterr()
    assert '1732' in out
