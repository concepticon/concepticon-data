# CLLD Concepticon

The data underlying the [Concepticon](http://concepticon.clld.org) of the [CLLD](http://clld.org) project is maintained in this repository. Here, you can find 

* [previous and current releases](https://github.com/clld/concepticon-data/releases), 
* [issues we are trying to handle](https://github.com/clld/concepticon-data/issues), as well as the 
* [current unreleased form of the data](https://github.com/clld/concepticon-data/tree/master/concepticondata).

The repository also contains the sources of [`pyconcepticon`](#pyconcepticon), a python package providing an API to access and manipulate the Concepticon data.


## Concepticon Data

* For an overview on the status of all currently linked conceptlists, see [here](https://github.com/clld/concepticon-data/blob/master/concepticondata/conceptlists/README.md).
* For basic information on metadata, see [here](https://github.com/clld/concepticon-data/blob/master/concepticondata/concept_set_meta/README.md).
* For information on how you can contribute to the project or profit from the data sources we offer, see [here](https://github.com/clld/concepticon-data/blob/master/CONTRIBUTING.md).


### Data Structure

- **conceptlists/** folder contains conceptlists with links to IDs in concepticon.tsv, the 
  lists are named after the first person who proposed them, the year of the reference publication 
  in which we extracted them, and the number of concepts. All these three parts of information 
  are separated by a dash. Furthermore, in cases where two lists would have an identical name, 
  we add alphabetical letters to the lists to distinguish them. Files need to have the columns 
  "GLOSS" (some still have "ENGLISH" instead, but this needs to be changed), additionally, most 
  (if not all files) have a "NUMBER" field indicating the number in the reference, which is also 
  important for ordering the entries as given in the original source. Additional columns are more 
  or less free to the user, but we tried to be consistent.
- **conceptlists.tsv** contains metadata about the lists in **conceptlists/**.
- **references/references.bib** the bibtex file showing links to all concept lists (bibtex-key 
  identical to the name of the conceptlist file, without file-ending. File further contains links 
  to the references  in which the conceptlists were published (references stored in the "crossref" field). 
- **sources/** contains pdf-files of each conceptlist (only the list-parts, not the full publications 
  for copyright reasons), naming is the same as for the conceptlists, but with the ending ".pdf" instead of ".tsv".
- **concepticon.tsv** the backbone concept list. All concepts from individual concept lists are linked to entries in this file.
- **concept_set_meta/** contains lists of metadata, relating concept sets to additional information, e.g. on Wikipedia. 
  These lists are described by accompanying metadata files following the recommendations of the 
  [Model for Tabular Data and Metadata on the Web](http://www.w3.org/TR/tabular-data-model/).


<a id="pyconcepticon"> </a>
## `pyconcepticon`

[![Build Status](https://travis-ci.org/clld/concepticon-data.svg?branch=master)](https://travis-ci.org/clld/concepticon-data)

### Installation

`pyconcepticon` can be installed from [PyPI](https://pypi.python.org/pypi), e.g. using pip
```
pip install pyconcepticon
```
This will install the latest released version.

Alternatively (in particular if you want to hack on `pyconcepticon`), you can install from a clone of this repository;
i.e. running
```
python setup.py develop
```
in the top-level directory of your clone of `concepticon-data`.


### Usage

To use `pyconcepticon` you must have a local copy of the Concepticon data, i.e. either

* the sources of a [released version](https://github.com/clld/concepticon-data/releases), as provided in the **Downloads** section of a release, or
* a clone of this repository (or your personal fork of it).

Assuming you have downloaded release 1.0.2 and unpacked the sources to a directory `concepticon-data-1.0.2`, you can access
the data as follows:
```python
>>> from pyconcepticon.api import Concepticon
>>> concepticon = Concepticon('concepticon-data-1.0.2')
>>> clists = concepticon.conceptlists()
>>> for item in clists[0].items():
...     print '%s: %s' % item
... 
ID: Kessler-2001-200
AUTHOR: Kessler, Brett
YEAR: 2001
LIST_SUFFIX: 
ITEMS: 200
TAGS: basic
SOURCE_LANGUAGE: English
TARGET_LANGUAGE: global
URL: 
REFS: Kessler2001
PDF: 
NOTE: This list was used to test various methods for the proof of language relationship. It is supposed to follow strictly the [200-item list of Swadesh (1952)](:ref:Swadesh-1952-200).
PAGES: 202-258
>>> concepts = concepticon.conceptlist(clists[0]['ID'])
>>> len(concepts)
200
>>> for item in concepts[0].items():
...     print '%s: %s' % item
... 
ID: Kessler-2001-200-1
NUMBER: 1
ENGLISH: all
CONCEPTICON_ID: 98
CONCEPTICON_GLOSS: ALL
```
