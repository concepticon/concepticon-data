# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.path import Path

from concepticondata.util import data_path, REPOS_PATH, tsv_items


class Concepticon(object):
    def __init__(self, repos=None):
        self.repos = Path(repos) if repos else REPOS_PATH

    def data_path(self, *comps):
        return data_path(*comps, **{'repos': self.repos})

    def conceptlist(self, id_):
        return tsv_items(self.data_path('conceptlists', id_ + '.tsv'), ordered=True)
