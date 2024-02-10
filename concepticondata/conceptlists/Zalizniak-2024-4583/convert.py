from pycldf import Dataset
from csvw.dsv import UnicodeWriter, UnicodeDictReader
import json


with UnicodeDictReader("raw/parameters.csv") as reader:
    data = [row for row in reader]

table = [["ID", "NUMBER", "ENGLISH", "CONCEPTICON_ID", "CONCEPTICON_GLOSS",
          "LINKED_CONCEPTS", "TARGET_CONCEPTS", "SHIFTS", "DEFINITION",
          "ALIAS", "DOMAIN"]]
id2id = {}
for row in data:
    id2id[row["ID"]] = "Salizniak-2024-4583-" + row["Number"]

for row in data:
    links = []
    for t in json.loads(row["Linked_Concepts"]):
        t["ID"] = id2id[t["ID"]]
        links += [t]
    targets = []
    for t in json.loads(row["Target_Concepts"]):
        t["ID"] = id2id[t["ID"]]
        targets += [t]

    table += [[id2id[row["ID"]], row["Number"], row["Name"],
               row["Concepticon_ID"], row["Concepticon_Gloss"],
               json.dumps(links), json.dumps(targets), row["Shifts"],
               row["Definition"], row["Alias"], row["Domain"]]]
    
with UnicodeWriter("Zalizniak-2024-4583.tsv", delimiter="\t") as writer:
    for row in table:
        writer.writerow(row)
