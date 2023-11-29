from csvw.dsv import UnicodeDictReader, UnicodeWriter
from pysem import to_concepticon
from collections import defaultdict
import json

list_name = "Winter-2022-99"

# must correct for error in data
correct = {
        "soil": "soil/earth",
        "Milky Way": "milky way",
        "river": "river/stream",
        "fog": "fog/mist",
        "(molar) tooth": "tooth"
        }

# read in data
data = defaultdict(list)
with UnicodeDictReader("raw/asymmetry.csv") as reader:
    for row in reader:
        concept = correct.get(row["ConceptComplete"], row["ConceptComplete"])
        if row["ID"] == "65" and row["Word"] == "river":
            concept = "river/stream"
        data[concept] += [row]

# populate the table
# give an identifier to the concept
row2idx = {}
for i, (concept, row) in enumerate(data.items()):
    idx = i+1
    row2idx[concept] = idx

# create graph
graph = defaultdict(lambda: {"sources": [], "targets": []})
for concept, rows in data.items():
    # add info on 
    for row in rows:
        oma, omar, polysemy = (
                int(row["OvertMarking"]),
                int(row["OvertMarkingReverse"]),
                int(row["Polysemy"]))
        source, target = list(map(lambda x: correct.get(x, x),
                                  row["PairName"].split("~")))
        source_id, target_id = list(map(
            lambda x: list_name + "-{0}".format(row2idx[x]),
            [source, target]))

        source_json = {
                "name": source,
                "id": source_id,
                "polysemy": polysemy,
                "overt_marking": oma
                }
        target_json = {
                "name": target,
                "id": target_id,
                "polysemy": polysemy,
                "overt_marking": oma
                }
        if concept == source:
            graph[concept]["targets"] += [target_json]
            graph[concept]["sources"] += [{
                k: omar if k == "overt_marking" else v for k, v in target_json.items()}]
        else:
            graph[concept]["sources"] += [source_json]
            graph[concept]["targets"] += [{
                k: omar if k == "overt_marking" else v for k, v in source_json.items()}]
            

with open("edges.tsv", "w") as f:
    f.write("Source\tTarget\tPolysemy\tOvertMarking\n")
    for node in graph:
        if graph[node]["targets"]:
            for target in graph[node]["targets"]:
                f.write("{0}\t{1}\t{2}\t{3}\n".format(
                    node,
                    target["name"],
                    target["polysemy"],
                    target["overt_marking"]))


with UnicodeWriter(list_name + ".tsv", delimiter="\t") as writer:
    writer.writerow(
            [        
             "ID",
             "NUMBER",
             "ENGLISH",
             "CONCEPTICON_ID",
             "CONCEPTICON_GLOSS",
             "SOURCE_CONCEPTS",
             "TARGET_CONCEPTS",
             ])

    table = []
    for concept in graph:
        # get concept mappings
        mappings = to_concepticon([{"gloss": concept}])[concept]
        if mappings:
            cid, cgl = mappings[0][0], mappings[0][1]
        else:
            cid, cgl = "", ""
        if concept == "meteroid":
            cid = "2288"
            cgl = "METEROID (SHOOTING OR SHINING STAR)"
        table += [[
            list_name + "-{0}".format(row2idx[concept]),
            str(row2idx[concept]),
            concept,
            cid, 
            cgl,
            json.dumps(graph[concept]["sources"]),
            json.dumps(graph[concept]["targets"]),
            ]]
    for row in sorted(table, key=lambda x: int(x[1])):
        writer.writerow(row)
