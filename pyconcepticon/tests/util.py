# coding: utf8
from __future__ import unicode_literals, print_function, division
from unittest import TestCase

from clldutils.path import Path


class TestWithFixture(TestCase):
    def fixture_path(self, *comps):
        return Path(__file__).parent.joinpath('fixtures', *comps)
