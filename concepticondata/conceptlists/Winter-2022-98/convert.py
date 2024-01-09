import pathlib
import collections

from csvw.dsv import reader
from pysem import to_concepticon
from pyconcepticon.util import ConceptlistWithNetworksWriter

# must correct for error in data
correct = {
    "soil": "soil/earth",
    "Milky Way": "milky way",
    "river": "river/stream",
    "fog": "fog/mist",
    "(molar) tooth": "tooth",
    "stomach": "belly/stomach"
}

map_concepts = {
    "pupil": ["1658", "PUPIL"],
    "straw/hay": ["2299", "STRAW"],
    "spring": ["849", "SPRING (OF WATER)"],
    "meteoroid": ["2288", "METEROID (SHOOTING OR SHINING STAR)"],
}

# read in data
data = collections.defaultdict(list)
for row in reader("raw/asymmetry.csv", dicts=True):
    concept = correct.get(row["ConceptComplete"], row["ConceptComplete"])
    if row["ID"] == "65" and row["Word"] == "river":
        concept = "river/stream"
    data[concept].append(row)

row2idx = {concept: idx for idx, (concept, _) in enumerate(data.items(), start=1)}

graph = collections.defaultdict(lambda: {"sources": [], "targets": [], "linked": []})
for concept, rows in data.items():
    for row in rows:
        if row["PairName"] == "day~noon":
            oma, omar, polysemy = 3, 20, 0
        else:
            oma, omar, polysemy = (
                int(row["OvertMarking"]), int(row["OvertMarkingReverse"]), int(row["Polysemy"]))
        source, target = list(map(
            lambda x: correct.get(x, x), row["PairName"].split("~")))
        source_id, target_id = list(map(
            lambda x: "{}-{}".format(pathlib.Path(__file__).parent.name, row2idx[x]),
            [source, target]))

        source_json = {"NAME": source, "ID": source_id, "OvertMarking": oma}
        target_json = {"NAME": target, "ID": target_id, "OvertMarking": oma}
        if concept == source:
            links_json = {"NAME": target, "ID": target_id, "Polysemy": polysemy}
        elif concept == target:
            links_json = {"NAME": source, "ID": source_id, "Polysemy": polysemy}
        if concept == source:
            graph[concept]["targets"] += [target_json]
            graph[concept]["sources"] += [{
                k: omar if k == "OvertMarking" else v for k, v in target_json.items()}]
        else:
            graph[concept]["sources"] += [source_json]
            graph[concept]["targets"] += [{
                k: omar if k == "OvertMarking" else v for k, v in source_json.items()}]
        graph[concept]["linked"] += [links_json]

with ConceptlistWithNetworksWriter(pathlib.Path(__file__).parent.name) as table:
    for concept in graph:
        # get concept mappings
        if concept in map_concepts:
            cid, cgl = map_concepts[concept]
        else:
            mappings = to_concepticon([{"gloss": concept}])[concept]
            cid, cgl = (mappings[0][0], mappings[0][1]) if mappings else ("", "")
        table.append(collections.OrderedDict([
            ('NUMBER', str(row2idx[concept])),
            ('ENGLISH', concept),
            ('CONCEPTICON_ID', cid),
            ('CONCEPTICON_GLOSS', cgl),
            ('SOURCE_CONCEPTS', graph[concept]["sources"]),
            ('TARGET_CONCEPTS', graph[concept]["targets"]),
            ('LINKED_CONCEPTS', graph[concept]["linked"]),
        ]))
