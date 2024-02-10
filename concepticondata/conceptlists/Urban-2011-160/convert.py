import pathlib
import collections
from csvw.dsv import UnicodeDictReader

from pyconcepticon import models
from pyconcepticon.util import ConceptlistWithNetworksWriter

# get concept to concepticon ID to have all data at hand
urban = models.Conceptlist.from_file("raw/Urban-2011-160.tsv")
concept2id = {concept.english: concept.id for concept in urban.concepts.values()}

# get indo-aryan shifts

reps = {"mirrow": "mirror", "straw/hay": "straw", "cheeck": "cheek"}
iashifts = collections.defaultdict(dict)
with UnicodeDictReader(
        pathlib.Path(__file__).parent / "raw" / "indo-aryan-shifts.tsv",
        delimiter="\t") as reader:
    for row in reader:
        iashifts[reps.get(row["Source"], row["Source"])][reps.get(
                row["Target"],
                row["Target"])] = row["ID"]


with ConceptlistWithNetworksWriter(pathlib.Path(__file__).parent.name) as table:
    linked_concepts = {concept.id: [] for concept in
                       urban.concepts.values()}
    targeted_concepts = {concept.id: [] for concept in
                         urban.concepts.values()}
    for concept in urban.concepts.values():
        targets, links = [], []
        if concept.english in iashifts and not concept.attributes["semantic_change"]:
            for target, idx in iashifts[concept.english].items():
                targeted_concepts[concept.id] += [{
                    "ID": concept2id[target],
                    "NAME": target,
                    "OvertMarking": 0,
                    "IndoAryanShift": 1,
                    "ShiftID": idx
                    }]
        if concept.attributes["semantic_change"]:
            # get the information, split by space
            for text in concept.attributes["semantic_change"].split("; "):
                # parse the data now
                data_a, data_b = text.split("» (")
                number = data_a.split(" ")[0][1:-1]
                source = data_a.split(">")[0].split("«")[1][:-2]
                target = data_a.split(">")[1].strip()[1:]
                polysemies = data_b.split(" ")[0]
                overt = data_b.split(", ")[1].split(" ")[0]
                # check for ia shift
                attested_shift = 0
                if concept.english in iashifts:
                    if reps.get(target, target) in iashifts[concept.english]:
                        attested_shift = 1
                targeted_concepts[concept.id] += [{
                    "ID": concept2id[reps.get(target, target)],
                    "NAME": reps.get(target, target),
                    "OvertMarking": int(overt),
                    "IndoAryanShift": attested_shift,
                    "ShiftID": int(number) + 1}]
                linked_concepts[concept.id] += [{
                    "ID": concept2id[reps.get(target, target)],
                    "NAME": reps.get(target, target),
                    "Polysemy": int(polysemies),
                    "ShiftID": int(number)+ 1}]
                linked_concepts[concept2id[reps.get(target, target)]] += [{
                    "ID": concept.id,
                    "NAME": concept.english,
                    "Polysemy": int(polysemies),
                    "ShiftID": int(number) + 1}]

    for concept in urban.concepts.values():
        row = collections.OrderedDict([
            ('NUMBER', concept.number),
            ('ENGLISH', concept.english),
            ('CONCEPTICON_ID', concept.concepticon_id),
            ('CONCEPTICON_GLOSS', concept.concepticon_gloss),
            ('SEMANTIC_CLASS_ID', concept.attributes["semantic_class_id"]),
            ('CATEGORY', concept.attributes["category"]),
        ])
                
        row['TARGET_CONCEPTS'] = targeted_concepts[concept.id]
        row['LINKED_CONCEPTS'] = linked_concepts[concept.id]
        table.append(row)
