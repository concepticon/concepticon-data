import enum
import pathlib
import functools
import collections

import igraph
from pyconcepticon import Concepticon
from pyconcepticon.util import ConceptlistWithNetworksWriter


class Graphs(enum.Enum):  # We read data from three different CLICS graphs.
    Full = 1
    Affix = 2
    Overlap = 3


def node_dict(type_):  # The skeleton for a concept node.
    res = {'ID': '', 'NAME': ''}
    if type_ == 'LINKED':
        res.update({'{}{}'.format(Graphs.Full.name, s): 0 for s in ['Vars', 'Lngs', 'Fams']})
        res.update({'{}{}'.format(Graphs.Overlap.name, s): 0 for s in ['Vars', 'Lngs', 'Fams']})
    else:
        res.update({'{}{}'.format(Graphs.Affix.name, s): 0 for s in ['Vars', 'Lngs', 'Fams']})
    return res


concepts, label2id = {}, {}
for g in Graphs:
    graph = igraph.read("raw/colexification-{}.gml".format(g.name.lower()))
    if g == Graphs.Full:  # Initialize the concepts.
        c2i = {c.gloss: c.id for c in Concepticon().conceptsets.values()}
        for i, node in enumerate(graph.vs):
            data = node.attributes()
            label2id[data["label"]] = str(i + 1)
            concepts[label2id[data["label"]]] = collections.OrderedDict([
                ('NUMBER', label2id[data["label"]]),
                ('ENGLISH', data["label"]),
                ('CONCEPTICON_ID', c2i[data["label"]]),
                ('CONCEPTICON_GLOSS', data["label"]),
                ('VARIETY_COUNT', int(data["variety_count"])),
                ('LANGUAGE_COUNT', int(data["language_count"])),
                ('FAMILY_COUNT', int(data["family_count"])),
                ('LINKED_CONCEPTS', collections.defaultdict(functools.partial(node_dict, 'LINKED'))),
                ('TARGET_CONCEPTS', collections.defaultdict(functools.partial(node_dict, 'TARGET')))
            ])

    for edge in graph.es:  # Loop over the edges of the graph.
        if ((g != Graphs.Overlap and int(edge["family_count"]) > 1)
                or (g == Graphs.Overlap and int(edge["family_count"]) > 4)):  # Apply thresholds.
            sname, tname = graph.vs[edge.source]["label"], graph.vs[edge.target]["label"]
            sidx, tidx = label2id[sname], label2id[tname]
            jds = concepts[sidx]['TARGET_CONCEPTS' if g == Graphs.Affix else 'LINKED_CONCEPTS']
            target_idx = pathlib.Path(__file__).parent.name + "-" + tidx
            jds[target_idx]["ID"] = target_idx
            jds[target_idx]["NAME"] = tname
            jds[target_idx][g.name + "Vars"] = int(edge["variety_count"]) 
            jds[target_idx][g.name + "Lngs"] = int(edge["language_count"]) 
            jds[target_idx][g.name + "Fams"] = int(edge["family_count"])
            if g != Graphs.Affix:  # For non-Affix edges, we als add the reversed edge.
                jds = concepts[tidx]['LINKED_CONCEPTS']
                target_idx = pathlib.Path(__file__).parent.name + "-" + sidx
                jds[target_idx]["ID"] = target_idx
                jds[target_idx]["NAME"] = sname
                jds[target_idx][g.name + "Vars"] = int(edge["variety_count"]) 
                jds[target_idx][g.name + "Lngs"] = int(edge["language_count"]) 
                jds[target_idx][g.name + "Fams"] = int(edge["family_count"])

with ConceptlistWithNetworksWriter(pathlib.Path(__file__).parent.name) as table:
    for rid, row in sorted(concepts.items(), key=lambda x: int(x[1]['NUMBER'])):
        for type_ in ['TARGET', 'LINKED']:
            row[type_ + '_CONCEPTS'] = sorted(
                row[type_ + '_CONCEPTS'].values(),
                key=lambda x: int(x["ID"].split('-')[-1]))
        table.append(row)
