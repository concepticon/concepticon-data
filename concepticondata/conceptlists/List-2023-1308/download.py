from urllib.request import urlretrieve
import zipfile


urlretrieve(
    "https://github.com/lingpy/pacs/raw/main/examples/colexifications-graphs.zip",
    "raw/graphs.zip")

with zipfile.ZipFile("raw/graphs.zip", "r") as obj:
    obj.extractall(path="raw")
