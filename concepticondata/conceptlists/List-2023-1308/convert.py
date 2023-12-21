import pathlib
import collections

import igraph
from pyconcepticon import Concepticon
from pyconcepticon.util import ConceptlistWithNetworksWriter

c2i = {c.gloss: c.id for c in Concepticon().conceptsets.values()}

graphs = collections.OrderedDict([
    (key, igraph.read("raw/colexification-{}.gml".format(key.lower())))
    for key in ['Full', 'Affix', 'Overlap']])

label2id = {k.attributes()["label"]: str(i+1) for i, k in enumerate(graphs['Full'].vs)}

concepts = {}
for i, node in enumerate(graphs['Full'].vs):
    data = node.attributes()
    concepts[label2id[data["label"]]] = collections.OrderedDict([
        ('NUMBER', label2id[data["label"]]),
        ('ENGLISH', data["label"]),
        ('CONCEPTICON_ID', c2i[data["label"]]),
        ('CONCEPTICON_GLOSS', data["label"]),
        ('VARIETY_COUNT', int(data["variety_count"])),
        ('LANGUAGE_COUNT', int(data["language_count"])),
        ('FAMILY_COUNT', int(data["family_count"])),
        ('LINKED_CONCEPTS', collections.defaultdict(lambda: dict(
            ID="",
            NAME="",
            OverlapVars=0,
            OverlapLngs=0,
            OverlapFams=0,
            FullVars=0,
            FullLngs=0,
            FullFams=0
        ))),
        ('TARGET_CONCEPTS', collections.defaultdict(lambda: dict(
            ID="", NAME="", AffixVars=0, AffixLngs=0, AffixFams=0)))
    ])

valid_edges = collections.defaultdict(list)
selected_edges = collections.defaultdict(list)
for name, graph in graphs.items():
    name = {'Full': 'colexification', 'Affix': 'affixes', 'Overlap': 'overlap'}[name]
    for edge in graph.es:
        if ((name != "overlap" and edge["family_count"] > 1)
                or (name == "overlap" and edge["family_count"] > 4)):
            valid_edges[(
                label2id[graph.vs[edge.source]["label"]],
                label2id[graph.vs[edge.target]["label"]],
            )] += [(name, edge.attributes()["family_count"])]
            valid_edges[(
                label2id[graph.vs[edge.target]["label"]],
                label2id[graph.vs[edge.source]["label"]],
            )] += [(name, edge.attributes()["family_count"])]

for name, graph in graphs.items():
    print(name)
    for edge in graph.es:
        sname, tname = graph.vs[edge.source]["label"], graph.vs[edge.target]["label"]
        sidx, tidx = label2id[sname], label2id[tname]
        if (sidx, tidx) in valid_edges:
            jds = concepts[sidx]['TARGET_CONCEPTS' if name == 'Affix' else 'LINKED_CONCEPTS']
            target_idx = pathlib.Path(__file__).parent.name + "-" + tidx
            jds[target_idx]["ID"] = target_idx
            jds[target_idx]["NAME"] = tname
            jds[target_idx][name + "Vars"] = int(edge["variety_count"]) 
            jds[target_idx][name + "Lngs"] = int(edge["language_count"]) 
            jds[target_idx][name + "Fams"] = int(edge["family_count"])
        if name != "Affix":
            if (tidx, sidx) in valid_edges:
                jds = concepts[sidx]['TARGET_CONCEPTS' if name == 'Affix' else 'LINKED_CONCEPTS']
                target_idx = pathlib.Path(__file__).parent.name + "-" + sidx
                jds[target_idx]["ID"] = target_idx
                jds[target_idx]["NAME"] = sname
                jds[target_idx][name + "Vars"] = int(edge["variety_count"]) 
                jds[target_idx][name + "Lngs"] = int(edge["language_count"]) 
                jds[target_idx][name + "Fams"] = int(edge["family_count"])

with ConceptlistWithNetworksWriter(pathlib.Path(__file__).parent.name) as table:
    for row in sorted(concepts.values(), key=lambda x: int(x['NUMBER'])):
        for type_ in ['TARGET', 'LINKED']:
            row[type_ + '_CONCEPTS'] = sorted(
                row[type_ + '_CONCEPTS'].values(),
                key=lambda x: int(x["ID"].split('-')[-1]))
        table.append(row)
