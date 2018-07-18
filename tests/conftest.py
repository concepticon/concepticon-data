# coding: utf8
from __future__ import unicode_literals, print_function, division

import pytest
from clldutils.path import Path

from pyconcepticon.api import Concepticon


@pytest.fixture
def fixturedir():
    return Path(__file__).parent.joinpath('fixtures')


@pytest.fixture(scope='session')
def api():
    return Concepticon(Path(__file__).parent.joinpath('fixtures'))
