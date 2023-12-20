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
        "NUMBER",
        "ENGLISH",
        "CONCEPTICON_ID",
        "CONCEPTICON_GLOSS",
        "VARIETY_COUNT",
        "LANGUAGE_COUNT",
        "FAMILY_COUNT",
        "LINKED_CONCEPTS",
        "TARGET_CONCEPTS",
        ]

affix_graph = igraph.read("raw/colexification-affix.gml")
print("loaded affix graph")
full_graph = igraph.read("raw/colexification-full.gml")
print("loaded full graph")
overlap_graph = igraph.read("raw/colexification-overlap.gml")
print("loaded overlap graph")

label2id = {k.attributes()["label"]: str(i+1) for i, k in enumerate(full_graph.vs)}

concepts = {}
for i, node in enumerate(full_graph.vs):
    data = node.attributes()
    name = data["label"]
    idx = list_prefix + "-" + label2id[name]
    cid = c2i[name]
    edge = {}
    concepts[label2id[name]] = [
            idx,
            label2id[name],
            name, cid, name, 
            int(data["variety_count"]),
            int(data["language_count"]),
            int(data["family_count"]),
            defaultdict(lambda: {
                "ID": "",
                "NAME": "",
                "OverlapVars": 0,
                "OverlapLngs": 0,
                "OverlapFams": 0,
                "FullVars": 0,
                "FullLngs": 0,
                "FullFams": 0
                }),
            defaultdict(lambda: {
                "ID": "",
                "NAME": "",
                "AffixVars": 0,
                "AffixLngs": 0,
                "AffixFams": 0
                })
            ]

valid_edges = defaultdict(list)
common_edges = defaultdict(list)
selected_edges = {
        "colexification": [], 
        "affixes": [],
        "overlap": []}

for graph, name in [
        (full_graph, "colexification"), 
        (affix_graph, "affixes"),
        (overlap_graph, "overlap")]:
    for edge in graph.es:
        common_edges[(
            label2id[graph.vs[edge.source]["label"]],
            label2id[graph.vs[edge.target]["label"]])] += [(
                name, edge["family_count"])]
        common_edges[(
            label2id[graph.vs[edge.target]["label"]],
            label2id[graph.vs[edge.source]["label"]])] += [(
                name, edge["family_count"])]

        if (
                name != "overlap" and edge["family_count"] > 1
                ) or (
                        name == "overlap" and edge[
                            "family_count"] > 4):
            valid_edges[(
                label2id[graph.vs[edge.source]["label"]],
                label2id[graph.vs[edge.target]["label"]],
                )] += [(name, edge.attributes()["family_count"])]
            valid_edges[(
                label2id[graph.vs[edge.target]["label"]],
                label2id[graph.vs[edge.source]["label"]],
                )] += [(name, edge.attributes()["family_count"])]
            selected_edges[name] += [edge]


for graph, edgelist, name in [
        (full_graph, "colexification", "Full"), 
        (affix_graph, "affixes", "Affix"),
        (overlap_graph, "overlap", "Overlap")]:
    print(name)
    for edge in selected_edges[edgelist]:
        sid, tid = edge.source, edge.target
        sname, tname = (
                graph.vs[sid]["label"], 
                graph.vs[tid]["label"])
        sidx, tidx = label2id[sname], label2id[tname]
        if (sidx, tidx) in valid_edges:
            source = concepts[sidx]
            if name == "Affix":
                jds = source[-1]
            else:
                jds = source[-2]
            target_idx = list_prefix + "-" + tidx
            jds[target_idx]["ID"] = target_idx
            jds[target_idx]["NAME"] = tname
            jds[target_idx][name + "Vars"] = int(edge["variety_count"]) 
            jds[target_idx][name + "Lngs"] = int(edge["language_count"]) 
            jds[target_idx][name + "Fams"] = int(edge["family_count"])

        if edgelist in ["colexification", "overlap"]:
            if (tidx, sidx) in valid_edges:
                source = concepts[tidx]
                jds = source[-2]
                target_idx = list_prefix + "-" + sidx
                jds[target_idx]["ID"] = target_idx
                jds[target_idx]["NAME"] = sname
                jds[target_idx][name + "Vars"] = int(edge["variety_count"]) 
                jds[target_idx][name + "Lngs"] = int(edge["language_count"]) 
                jds[target_idx][name + "Fams"] = int(edge["family_count"])
            

with UnicodeWriter(list_prefix + ".tsv", delimiter="\t") as writer:
    writer.writerow(header)
    for concept in sorted(concepts, key=lambda x: int(concepts[x][1])):
        row = concepts[concept]
        row[-1] = json.dumps(
            sorted(row[-1].values(), key=lambda x: x["ID"]))
        row[-2] = json.dumps(
            sorted(row[-2].values(), key=lambda x: x["ID"]))
        writer.writerow(row)
