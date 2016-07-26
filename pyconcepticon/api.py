# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.path import Path

from pyconcepticon.util import REPOS_PATH, data_path, read_dicts


class Concepticon(object):
    def __init__(self, repos=None):
        self.repos = Path(repos) if repos else REPOS_PATH

    def data_path(self, *comps):
        return data_path(*comps, **{'repos': self.repos})

    def conceptsets(self):
        return read_dicts(self.data_path('concepticon.tsv'))

    def conceptlist(self, id_):
        return read_dicts(self.data_path('conceptlists', id_ + '.tsv'))
