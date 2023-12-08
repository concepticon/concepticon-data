from urllib.request import urlopen
import zipfile

with urlopen(
        "https://github.com/lingpy/pacs/raw/main/examples/colexifications-graphs.zip"
        ) as f:
    data = f.read()
with open("raw/graphs.zip", "wb") as f:
    f.write(data)

with zipfile.ZipFile("raw/graphs.zip", "r") as obj:
    obj.extractall(path="raw")


