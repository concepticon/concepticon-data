# *-* coding: utf-8 *-*
"""
Module provides functions for the handling of concept glosses in linguistic datasets.
"""
from __future__ import print_function, division, unicode_literals
import re
from itertools import product
from collections import defaultdict

import attr


@attr.s
class Gloss(object):
    main = attr.ib(default='')
    # the start character indicating a potential comment:
    comment_start = attr.ib(default='')
    # the comment (everything occurring in brackets in the input string:
    comment = attr.ib(default='')
    # the end character indicating the end of a potential comment:
    comment_end = attr.ib(default='')
    # the part of speech, in case this was specificied by a preceding "the" or a
    # preceding "to" in the mainpart of the string:
    pos = attr.ib(default='')
    # the prefix, that is, words, like, eg. "be", "in", which may precede the main
    # gloss in concept lists, as in "be quiet":
    prefix = attr.ib(default='')
    # the longest constituent, which is identical with the main part if there's no
    # whitespace in the main part, otherwise the longest part part of the main gloss
    # split by whitespace:
    longest_part = attr.ib(default='')
    # the original gloss (for the purpose of testing):
    gloss = attr.ib(default='')

    def similarity(self, other):
        # first-order-match: identical glosses
        if self.gloss == other.gloss:
            return 1
        # second-order match: identical main-parts
        if self.main == other.gloss or self.gloss == other.main or\
                self.main == other.main:
            # best match if pos matches
            return 2 if self.pos == other.pos else 3
        if self.longest_part == other.longest_part:
            return 4 if self.pos and self.pos == other.pos else 5
        if other.longest_part in self.main.split():
            return 6
        if self.longest_part in other.main.split():
            return 7


def parse_gloss(gloss):
    """
    Parse a gloss into its constituents by applying some general logic.

    Parameters
    ----------
    gloss : str
        The gloss as found in various sources (we assume that we are dealing
        with English glosses here.

    Returns
    -------
    A list of `Gloss` instances.

    Notes
    -----

    The basic purpose of this function is to provide a means to make it easier
    to compare meanings across different resources. Often, linguists will
    annotate their resources quite differently, and for one and the same
    concept, we may find very different glosses. The concept "kill [verb]", for
    example may be glossed as "to kill", "kill", "kill (v.)", "kill
    (somebody)", etc. In order to guarantee comparability, this function tries
    to use basic knowledge of glossing tendencies to disentangle the variety of
    glossing styles which can be found in the literature. Thus, in the case of
    "kill [verb]", the function will analyze the different strings as follows::

        >>> glosses = ["to kill", "kill", "kill (v.)", "kill (somebody)"]
        >>> for gloss in glosses:
        ...     parsed_gloss = parse_gloss(gloss)[0]
        ...     print(parsed_gloss.main, parsed_gloss.pos)
        kill verb
        kill
        kill verb
        kill

    As can be seen: it seeks to extract the most important part of the gloss
    and may thus help to compare different glosses across different resources.
    """
    G = []
    gpos = ''
    pos_markers = {'the': 'noun', 'a': 'noun', 'to': 'verb'}
    prefixes = ['be', 'in', 'at']
    abbreviations = [
        ('vb', 'verb'),
        ('v.', 'verb'),
        ('v', 'verb'),
        ('adj', 'adjective'),
        ('nn', 'noun'),
        ('n.', 'noun'),
        ('adv', 'adverb'),
        ('noun', 'noun'),
        ('verb', 'verb'),
        ('adjective', 'adjective'),
        ('cls', 'classifier')
    ]

    for constituent in re.split(',|;|/| or ', gloss):
        if constituent.strip():
            res = Gloss(gloss=gloss)
            mainpart = ''
            in_comment = False
            for char in constituent:
                if char in '([{（<':
                    in_comment = True
                    res.comment_start += char
                elif char in ')]}）>':
                    in_comment = False
                    res.comment_end += char
                else:
                    if in_comment:
                        res.comment += char
                    else:
                        mainpart += char

            mainpart = ''.join(m for m in mainpart if m not in '?!"¨:;,»«´“”*+-')\
                .strip().lower().split()

            # search for pos-markers
            if gpos:
                res.pos = gpos
            else:
                if len(mainpart) > 1 and mainpart[0] in pos_markers:
                    gpos = res.pos = pos_markers[mainpart.pop(0)]

            # search for strip-off-prefixes
            if len(mainpart) > 1 and mainpart[0] in prefixes:
                res.prefix = mainpart.pop(0)

            # check for a "first part" in case we encounter white space in the
            # data (and return only the largest string of them)
            res.longest_part = sorted(mainpart, key=lambda x: len(x))[-1]

            # search for pos in comment
            if not res.pos:
                cparts = res.comment.split()
                for p, t in sorted(abbreviations, key=lambda x: len(x[0]), reverse=True):
                    if p in cparts or p in mainpart or t in cparts or t in mainpart:
                        res.pos = t
                        break

            res.main = ' '.join(mainpart)
            G.append(res)

    return G

def concept_map2(from_, to, similarity_level=5, freqs=None):
    
    # get frequencies
    freqs = freqs or defaultdict(int)

    # extract glossing information from the data
    glosses = {'from': {}, 'to': {}}
    mapped = defaultdict(lambda : defaultdict(list))
    for l, key in [(from_, 'from'), (to, 'to')]:
        for i, concept in enumerate(l):
            for gloss in parse_gloss(concept):
                glosses[key][i] = gloss
                mapped[gloss.main][key] += [i]
    
    mapping = {}
    for k, v in mapped.items():
        if 'from' in v and 'to' in v:
            similarities = []
            current_sim = 10
            best = set()
            for i, j in product(v['from'], v['to']):
                sim = glosses['from'][i].similarity(glosses['to'][j]) or 10
                if sim < current_sim:
                    best = set([j])
                    current_sim = sim
                elif sim == current_sim:
                    best.add(j)
            mapping[i] = (sorted(best, key=lambda x:
                freqs.get(to[x], 0), reverse=True), sim)
    return mapping

            

def concept_map(from_, to, similarity_level=5):
    """
    Function compares two concept lists and outputs suggestions for mapping.

    Notes
    -----
    Idea is to take one conceptlist as the basic list and then to search for a
    plausible mapping of concepts in the second list to the first list. All
    suggestions can then be output in various forms, both with multiple matches
    excluded or included, and in textform or in other forms.

    What is important, regarding the output here, is, that the output contains
    all matches, including non-matched items which occur **in the second list
    but not in the first list**. Non-matched items which occur in the first
    list but not in the second list are ignored.
    """
    # extract glossing information from the data
    glosses = {'from': {}, 'to': {}}
    for l, key in [(from_, 'from'), (to, 'to')]:
        for i, concept in enumerate(l):
            glosses[key][i] = parse_gloss(concept)

    # now that we have prepared all the glossed list as planned, we compare them item by
    # item and check for similarity
    sims = []
    for i, fglosses in glosses['from'].items():
        for fgloss in fglosses:
            for j, tglosses in glosses['to'].items():
                for tgloss in tglosses:
                    sim = fgloss.similarity(tgloss)
                    if sim and sim <= similarity_level:
                        sims.append((i, j, sim))

    # we keep track of which target concepts have already been chosen as best matches:
    consumed = set()
    best = {}
    # go through *all* matches from best to worst:
    for i, j, sim in sorted(sims, key=lambda x: x[2]):
        if i not in best and j not in consumed:
            best[i] = (j, sim)
            consumed.add(j)

    #for i, concept in enumerate(from_):
    #    if i in best:
    #        print('{0} -{1}-> {2}'.format(concept, best[i][1], to[best[i][0]]))
    #    else:
    #        print('{0} -> ?'.format(concept))

    return best
