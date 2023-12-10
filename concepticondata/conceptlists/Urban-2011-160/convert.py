from pyconcepticon import Concepticon, models
import json
from csvw.dsv import UnicodeWriter

# get concept to concepticon ID to have all data at hand
urban = models.Conceptlist.from_file("raw/Urban-2011-160.tsv")
concept2id = {}
for concept in urban.concepts.values():
    concept2id[concept.english] = concept.id

reps = {
        "mirrow": "mirror",
        "straw/hay": "straw",
        "cheeck": "cheek",
        }

table = []
for concept in urban.concepts.values():
    row = [
            concept.id,
            concept.number,
            concept.english,
            concept.concepticon_id,
            concept.concepticon_gloss,
            concept.attributes["semantic_class_id"],
            concept.attributes["category"],
            ]
    targets = []
    if concept.attributes["semantic_change"]:
        print(concept.attributes["semantic_change"])
        # get the information, split by space
        targets = []
        for text in concept.attributes["semantic_change"].split("; "):
            # parse the data now
            data_a, data_b = text.split("» (")
            number = data_a.split(" ")[0][1:-1]
            source = data_a.split(">")[0].split("«")[1][:-2]
            target = data_a.split(">")[1].strip()[1:]
            polysemies = data_b.split(" ")[0]
            overt = data_b.split(", ")[1].split(" ")[0]
            targets += [{
                "ID": concept2id[reps.get(target, target)],
                "NAME": reps.get(target, target),
                "Polysemy": int(polysemies),
                "OvertMarking": int(overt),
                "ShiftID": int(number)}]
    row += [json.dumps(targets)]
    table += [row]

with UnicodeWriter("Urban-2011-160.tsv", delimiter="\t") as writer:
    writer.writerow(
            [
                "ID",
                "NUMBER",
                "ENGLISH", "CONCEPTICON_ID", "CONCEPTICON_GLOSS",
                "SEMANTIC_CLASS_ID", "CATEGORY", "TARGET_CONCEPTS"])
    for row in table:
        writer.writerow(row)

