from pycldf import Dataset
from csvw.dsv import UnicodeWriter, UnicodeDictReader
import json
from pyconcepticon.util import ConceptlistWithNetworksWriter
import pathlib
import collections


with UnicodeDictReader("raw/parameters.csv") as reader:
    data = [row for row in reader]

id2id = {}
for row in data:
    id2id[row["ID"]] = "Salizniak-2024-4583-" + row["Number"]

with ConceptlistWithNetworksWriter(
        pathlib.Path(__file__).parent.name) as table:

    for row in data:
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

