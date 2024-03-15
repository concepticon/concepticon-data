import pathlib
import collections

from pyconcepticon import models
from pyconcepticon.util import ConceptlistWithNetworksWriter

dss = models.Conceptlist.from_file("raw/Zalizniak-2020-2590.tsv")

num2id = {concept.number: concept.id for concept in dss.concepts.values()}
num2name = {concept.number: concept.english for concept in dss.concepts.values()}

with ConceptlistWithNetworksWriter(pathlib.Path(__file__).parent.name) as table:
    graph = {}
    for concept in dss.concepts.values():
        links = concept.attributes["links"].split()
        dirs = concept.attributes["directions"].split()
        shifts = concept.attributes["urls"].split()
        weights = concept.attributes["weights"].split()
    
        polysemy, sources, targets = [], [], []
        for link, direction, shift, weight in zip(links, dirs, shifts, weights):
            if direction in ['—', '↔']:
                polysemy += [{
                    "ID": num2id[link],
                    "NAME": num2name[link],
                    "Weight": weight,
                }]
            elif direction == "→":
                targets += [{
                    "ID": num2id[link],
                    "NAME": num2name[link],
                    "Weight": weight,
                }]
        table.append(collections.OrderedDict([
            ('NUMBER', concept.number),
            ('ENGLISH', concept.english),
            ('CONCEPTICON_ID', concept.concepticon_id),
            ('CONCEPTICON_GLOSS', concept.concepticon_gloss),
            ('RANK', concept.attributes["rank"]),
            ('DEGREE', concept.attributes["degree"]),
            ('WEIGHTED_DEGREE', concept.attributes["weighted_degree"]),
            ('LINKED_CONCEPTS', polysemy),
            ('TARGET_CONCEPTS', targets),
        ]))
