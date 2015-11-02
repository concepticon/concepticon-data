# concepticon-data

[![Build Status](https://travis-ci.org/clld/concepticon-data.svg?branch=master)](https://travis-ci.org/clld/concepticon-data)

## Structure of current data

- **conceptlists/** folder contains conceptlists with links to OMEGAWIKI and concepticon.tsv (all in column "OMEGAWIKI"), the lists are named after the first person who proposed them, the year of the reference publication in which we extracted them, and the number of concepts. All these three parts of information are separated by a dash. Furthermore, in cases where two lists would have an identical name, we add alphabetical letters to the lists to distinguish them. Files need to have the columns "GLOSS" (some still have "ENGLISH" instead, but this needs to be changed) and "OMEGAWIKI", additionally, most (if not all files) have a "NUMBER" field indicating the number in the reference, which is also important for ordering the entries as given in the original source. Additional columns are more or less free to the user, but we tried to be consistent.
- **references/references.bib** the bibtex file showing links to all concept lists (bibtex-key identical to the name of the conceptlist file, without file-ending. File further contains links to the references  in which the conceptlists were published (references stored in the "crossref" field). 
- **sources/** contains pdf-files of each conceptlist (only the list-parts, not the full publications for copyright reasons), naming is the same as for the conceptlists, but with the ending ".pdf" instead of ".tsv".
- **concepticon.tsv** basically also a conceptlist, but we use it as the basic reference which contains glosses, links to WOLD (if they are given), links to OMEGAWIKI, and some additional information.


## Note on concept list "types"

It is not easy to classify the various types of concept lists, but we try anyway to come up with an initial schema. Here's the current types which are distinguished along with their abbreviations:

* an: **annotated concept list**, a concept list that contains any level of annotation added to the concepts it contains. Typical example are those lists which additionally order the concepts into semantic fields, like "Bowern-208-207", or add colexification information, like "List-2015-1280". 
* av: **areal vocabulary list**, a concept list that was designed for the purpose of subgrouping in a specific area, like "Matisoff-1978-200", or "Norman-2003-40"
* bv: **basic vocabulary list**, the most typical case of a conceptlist.
* h: **historical concept list**, a list which we included for historical reasons, and where due to the historical character of the concept list, the reasons for the compilation are not necessarily clear
* hi: **HiHi vocabulary list**, following the terminology of [McMahon and McMahon (2005)](http://bibliography.lingpy.org?key=McMahon2005), this is the most stable part of a given basic vocabulary list.
* lo: **LoLo vocabulary list**, following the terminology of [McMahon and McMahon (2005)](http://bibliography.lingpy.org?key=McMahon2005), this is the least stable part of a given basic vocabulary list.
* ls: **Less stable sublist**, in contrast to the practice by [McMahon and McMahon (2005)](http://bibliography.lingpy.org?key=McMahon2005), wo extract two small lists from a baselist, which do not cover the whole baselist, less stable sublists are based on a complete division of a given wordlist in two parts. Paradigmatic examples are "Yakhhontov-1991-100", which is divided into "Yakhontov-1991-35" and "Yakhontov-1991-65". 
* q: **questionnaire**, a term which is reserved for all lists which have a larger amount of lexical items and have been created for specific purposes other than lexicocstatistical subgrouping or cognate detection. Questionnaires are often typical for a given area or language family.
* rank: **ranked concept list**, a list which can be ranked according to some meta-data that the list provides, like "Tadmor-2008-100", or "Starostin-2007-110".
* sp: **special purpose list**, a dummy category to include all lists which can currently not be sufficiently classified. 
* us: **ultra stable concept list**, a list that was compiled with the idea in mind to list concepts whose form-meaning relation is supposed to be very stable.
* ms: **more stable sublist**, the counterpart of a **less stable sublist**, that this the upper division of a given basic vocabulary list, which is supposed to be more stable than the lower division.

Note that we try to avoid assigning multiple "type" labels to one and the same list, but that we do not discourage that automatically, since there are well a few lists which have been compiled with different goals in mind.

