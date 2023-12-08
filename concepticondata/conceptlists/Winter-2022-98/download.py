from urllib.request import urlopen

with urlopen(
        "https://github.com/bodowinter/asymmetry/raw/master/data/asymmetry.csv"
        ) as f:
    data = f.read().decode("utf-8")
with open("raw/asymmetry.csv", "w") as f:
    f.write(data)


