from csvw.dsv import UnicodeDictReader, UnicodeWriter
from pyconcepticon import Concepticon, models
import json
from collections import defaultdict

dss = models.Conceptlist.from_file("raw/Zalizniak-2020-2590.tsv")

num2id, num2name = {}, {}
for concept in dss.concepts.values():
    num2id[concept.number] = concept.id
    num2name[concept.number] = concept.english

table = []

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
                "Shifts": "https://datsemshift.ru/" + shift
                }]
        elif direction == "→":
            targets += [{
                "ID": num2id[link],
                "NAME": num2name[link],
                "Weight": weight,
                "Shifts": "https://datsemshift.ru/" + shift
                }]
    row = [
            concept.id,
            concept.number,
            concept.english,
            concept.concepticon_id,
            concept.concepticon_gloss,
            concept.attributes["rank"],
            concept.attributes["degree"],
            concept.attributes["weighted_degree"],
            json.dumps(polysemy),
            json.dumps(targets)
            ]
    table += [row]

with UnicodeWriter("Zalizniak-2020-2590.tsv", delimiter="\t") as writer:
    writer.writerow([
        "ID", "NUMBER", "ENGLISH", "CONCEPTICON_ID", "CONCEPTICON_GLOSS", "RANK", "DEGREE", "WEIGHTED_DEGREE",
        "LINKED_CONCEPTS", "TARGET_CONCEPTS"])
    for row in table:
        writer.writerow(row)

