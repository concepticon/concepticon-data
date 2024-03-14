import json
import pathlib
import collections

from pycldf import Dataset
from csvw.dsv import UnicodeWriter, reader
from pyconcepticon.util import ConceptlistWithNetworksWriter

rdir = pathlib.Path(__file__).parent / "raw"
data = {row["Number"]: row for row in reader(rdir / "parameters.csv", dicts=True)}
concepts = {
    row["NUMBER"]: row for row in reader(rdir / "concepts-mapped.tsv", dicts=True, delimiter='\t')}
id2id = {row['ID']: "Zalizniak-2024-4583-" + row["Number"] for row in data.values()}

with ConceptlistWithNetworksWriter(pathlib.Path(__file__).parent.name) as table:
    for number, row_ in concepts.items():
        if number not in data:
            new_row = collections.OrderedDict([
                ("NUMBER", row_["NUMBER"]),
                ("ENGLISH", "*" + row_["ENGLISH"]),
                ("GLOSS_IN_SOURCE", row_["GLOSS_IN_SOURCE"]),
                ("DEFINITION", row_["DEFINITION"]),
                ("CONCEPTICON_ID", ""),
                ("CONCEPTICON_GLOSS", ""),
                ("SHIFTS", ""),
                ("DEFINITION", row_["DEFINITION"]),
                ("ALIAS", row_["ALIAS"]),
                ("DOMAIN", row_["DOMAIN"]),
                ("TARGET_CONCEPTS", []),
                ("LINKED_CONCEPTS", []),
                ])
        else:
            row = data[number]
            new_row = collections.OrderedDict([
                ("NUMBER", row["Number"]),
                ("ENGLISH", row["Name"]),
                ("GLOSS_IN_SOURCE", row["Gloss_in_Source"]),
                ("CONCEPTICON_ID", row["Concepticon_ID"]),
                ("CONCEPTICON_GLOSS", row["Concepticon_Gloss"]),
                ("SHIFTS", row["Shifts"]),
                ("DEFINITION", row["Definition"]),
                ("ALIAS", row["Alias"]),
                ("DOMAIN", row["Domain"])])
            links = []
            for t in json.loads(row["Linked_Concepts"]):
                t["ID"] = id2id[t["ID"]]
                links += [t]
            targets = []
            for t in json.loads(row["Target_Concepts"]):
                t["ID"] = id2id[t["ID"]]
                targets += [t]
            new_row["TARGET_CONCEPTS"] = targets
            new_row["LINKED_CONCEPTS"] = links
        table.append(new_row)

