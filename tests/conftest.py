# coding: utf8
from __future__ import unicode_literals, print_function, division

import pytest
from clldutils.path import Path


@pytest.fixture
def fixturedir():
    return Path(__file__).parent.joinpath('fixtures')
