import igraph
from collections import defaultdict
import json
from csvw.dsv import UnicodeWriter
from pyconcepticon import Concepticon

con = Concepticon()
c2i = {c.gloss: c.id for c in con.conceptsets.values()}

list_prefix = "List-2023-1308"
header = [
        "ID",
        "ENGLISH",
        "CONCEPTICON_ID",
        "CONCEPTICON_GLOSS",
        "TARGET_CONCEPTS",
        "VARIETY_COUNT",
        "LANGUAGE_COUNT",
        "FAMILY_COUNT"
        ]


graph = igraph.read("raw/colexification-affix.gml")

concepts = {}
for i, node in enumerate(graph.vs):
    data = node.attributes()
    idx = list_prefix + "-" + str(int(data["id"])+1)
    name = data["label"]
    cid = c2i[name]
    edge = {}
    concepts[int(data["id"])] = [
            idx,
            name, cid, name, 
            [],
            data["variety_count"],
            data["language_count"],
            data["family_count"]]

for edge in graph.es:
    data = edge.attributes()
    sid, tid = edge.source, edge.target
    source = concepts[sid]
    jsd = source[4]
    new_data = {
            "id": list_prefix + "-" + str(tid+1),
            "name": graph.vs[tid].attributes()["label"],
            "variety_count": data["variety_count"],
            "family_count": data["family_count"],
            "language_count": data["language_count"]}
    jsd.append(new_data)

with UnicodeWriter(list_prefix + ".tsv", delimiter="\t") as writer:
    writer.writerow(header)
    for concept in sorted(concepts):
        row = concepts[concept]
        row[4] = json.dumps(row[4])
        writer.writerow(row)
