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
iashifts = {}
with UnicodeDictReader(
        pathlib.Path(__file__).parent / "raw" / "indo-aryan-shifts.tsv",
        delimiter="\t") as reader:
    for row in reader:
        if row["Direction"] == "1":
            iashifts[reps.get(row["Source"], row["Source"])] = reps.get(
                    row["Target"],
                    row["Target"])
        else:
            iashifts[reps.get(row["Target"], row["Target"])] = reps.get(
                    row["Source"],
                    row["Source"])


with ConceptlistWithNetworksWriter(pathlib.Path(__file__).parent.name) as table:
    for concept in urban.concepts.values():
        row = collections.OrderedDict([
            ('NUMBER', concept.number),
            ('ENGLISH', concept.english),
            ('CONCEPTICON_ID', concept.concepticon_id),
            ('CONCEPTICON_GLOSS', concept.concepticon_gloss),
            ('SEMANTIC_CLASS_ID', concept.attributes["semantic_class_id"]),
            ('CATEGORY', concept.attributes["category"]),
        ])
        targets, links  = [], []
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
                targets += [{
                    "ID": concept2id[reps.get(target, target)],
                    "NAME": reps.get(target, target),
                    "OvertMarking": int(overt),
                    "ShiftID": int(number)}]
                links += [{
                    "ID": concept2id[reps.get(target, target)],
                    "NAME": reps.get(target, target),
                    "Polysemy": int(polysemies),
                    "AttestedShift": attested_shift,
                    "ShiftID": int(number)}]
        row['TARGET_CONCEPTS'] = targets
        row['LINKED_CONCEPTS'] = links
        table.append(row)
