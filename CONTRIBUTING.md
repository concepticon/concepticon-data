﻿# How to Contribute to the CLLD Concepticon?

Contributing to the CLLD Concepticon is simple on the one hand and difficult on the other. If you are an experienced user of GitHub and know about the basic ideas behind pull requests and testing in Python, it will be easy to propose changes. Creating the change proposals, however, requires to study the way we encode data in the CLLD Concepticon. We recommend that you have a look at the workflows we created, since these may significantly ease the task of adding new concept lists, or changing the mappings we provide in existing ones.

## GitHub Pull Requests

We won't give you any detailed explanations here but just assume that you find all information you need in this excellent HowTo:

* https://gun.io/blog/how-to-github-fork-branch-and-pull-request

If you experience any problems, just let us know.

## Submitting Concept Lists

Let us assume you have a concept list which you would like to submit to our Concepticon, so that we can afterwards include it and link it. In this case, you could write us an email, but even better, you would open an issue using our [issue tracker](https://github.com/concepticon/concepticon-data/issues). Here, we collect and classify different kinds of issues. New concept lists are tagged accordingly, and [here](https://github.com/concepticon/concepticon-data/issues?q=is%3Aissue+is%3Aopen+label%3A%22new+concept+list%22) you can see all concept lists, which we would like to map but have not yet found time to include.

In our workflow, we distinguish different stages of concept list creation and indicate this with tags:

* [scanned](https://github.com/concepticon/concepticon-data/issues?q=is%3Aissue+is%3Aopen+label%3Ascanned) refers to those concept lists which are already available in a scanned version, so that we can start typing them off. Sometimes, concept lists are only available in some specific archive, and we don't have access to them immediately. In this case, our concept list issue is just tagged as "new concept list", not yet as "scanned".
* [typed](https://github.com/concepticon/concepticon-data/issues?q=is%3Aissue+is%3Aopen+label%3Atyped) refers to those concept lists which have already been digitized. 
* [formatted](https://github.com/concepticon/concepticon-data/issues?q=is%3Aissue+is%3Aopen+label%3Aformatted) refers to concept lists which have been already brought into the format needed for mapping. That is, they are given as TSV file, with one field indicating the number, one for the concept label, and additional fields indicating additional data as given in the concept list.

Once you opened an issue and provide us with the important information, we will tag the issue accordingly, and try to follow it up. If you have the list in a typed version, or even in a formatted version, you could directly attach it to your issue.

## Linking Concept Lists

Suppose you have prepared a dataset that contains a concept list and that you would like to submit to the Concepticon, or you have detected a concept list you deem important but which you don't find in our current collection: What are the steps you need to undertake to submit this list to us, and to share it with the whole community? A simple way is to open an issue about a missing concept list. If you do so, we will evaluate the proposal and see what we can do.
Naturally, we'd appreciate it even more if you could provide us with 
* a scanned version of the list, or even better
* a digitized (typed-off) version of the list, or even better
* a linked version of the list.
In all these cases, you could still just write an email or attach the list to the issue. But you could also create a branch from the Concepticon master branch (see "GitHub Pull Requests" above) and officially add the data. 
The advantage of this is that you could be listed as a contributor in the next of the yearly releases of the CLLD Concepticon. We guarantee acknowledgement of all authors of **linked versions of new missing concept lists**. We officially thank all people who provided scans and digitized versions on the website at https://concepticon.clld.org/contributors.

### Linking Concept Lists: The Manual Style

If you link a concept list manually, we will check automatically and manually that this has been done properly. However, if you follow our [beginner's guide for adding concept lists](https://calc.hypotheses.org/2225) your list should be in a good stage for a contribution. We recommend that you prepare your changes in text-files rather than spreadsheet programs. In order to link a concept list, you need to supply the following information:

* the concept list itself, which should be placed into the folder [conceptlists/](https://github.com/concepticon/concepticon-data/tree/master/concepticondata/conceptlists). Here, we follow the convention of naming the file according to the schema FirstAuthor-Year-NumberOfItems.tsv. If you have multiple lists published in the same article/book, disambiguation with a, b, and c is recommended. If two lists have the same author, year, and number of items, they must be disambiguated with a, b, c. Each list needs to have the following fields (the order is irrelevant):
  - ID: an identifier, following the schema FirstAuthor-Year-NumberOfItems-Number
  - NUMBER: a number for each item of your list which corresponds to the ID 
  - ENGLISH or GLOSS: use ENGLISH, if the original language is ENGLISH; use GLOSS, if the original entry of the concept label is another language and the gloss is your translation; at least one of the columns needs to be included in the concept list
  - CONCEPTICON_ID: either a valid ID of our Concepticon, or an empty field, if you don't know how to map it (we automatically compute the amount of missing links and indicate them for each concept list)
  - CONCEPTICON_GLOSS: the gloss corresponding to the CONCEPTICON_ID

Apart from this, you can add as many further columns as you want. Here, we have further conventions:
  - if you have translations of the gloss in different languages, label them accordingly (CHINESE, FRENCH, etc.)
  - if you have a ranked list, provide the RANK as an integer and name the field RANK
  - there are further "soft" conventions e.g. concerning the way additional metadata are handled, which you can inspect by having a look at the different concept lists which are already mapped (see for example [Luniewska-2016-299.tsv](https://github.com/concepticon/concepticon-data/blob/master/concepticondata/conceptlists/Luniewska-2016-299.tsv) and [the associcated metadata file](https://github.com/concepticon/concepticon-data/blob/master/concepticondata/conceptlists/Luniewska-2016-299.tsv-metadata.json))
* the reference, provided as a BibTex entry in the file [references.bib](https://github.com/concepticon/concepticon-data/blob/master/concepticondata/references/references.bib). Please use the schema FirstAuthorYear and add a, b, c, etc. if there are multiple entires for the same author and the same year, 
* a description of the basic characteristics of the list in the file [conceptlists.tsv](https://github.com/concepticon/concepticon-data/blob/master/concepticondata/conceptlists.tsv). Here, we recommend you to either contact us if there are further questions, or to just look up how we usually encode the respective values. Not all information is required, but it is our goal to always try to fill out as many cells for a new concept list as possible. 
* if you have a scan of your list which does not fall under the copyright law (no full books, but pages in which one can see the concept lists should be acceptable), please label it as FirstAuthorLastNameYear.pdf, add a note in `conceptlists.tsv` (PDF column), and post the PDF as a comment to @chrzyki in the pull request.

If you feel that you need to add new concepts which are currently missing in
Concepticon, please open an issue, and we will provide you with the relevant
information on how to add new concept set identifiers. Generally speaking, the
process of adding new concepts can be done by:

  - closely inspecting [the current list of concepts in Concepticon](https://github.com/concepticon/concepticon-data/blob/master/concepticondata/concepticon.tsv) and deciding whether a new concept is in fact required
  - adding a new concept at the end of the list, with [a semantic field](https://github.com/concepticon/concepticon-data/blob/52c789ecd2cc20cdeb3433e2b945f6f4bf53d9ad/concepticondata/concepticon.json#L27-L51), a
    definition, and [an ontological category](https://github.com/concepticon/concepticon-data/blob/52c789ecd2cc20cdeb3433e2b945f6f4bf53d9ad/concepticondata/concepticon.json#L53-L59). However, please open an issue first.
  - checking whether the newly added concept can be applied to existing lists
    with: `concepticon notlinked --gloss "NEW_CONCEPT_GLOSS"`

Please do not hesitate to ask us if there are any further questions.

### Using automatic mapping software

NOTE: The `concepticon` command takes an argument `--repos` where you can specify
a path to the clone of `concepticon-data` that you want to work with. This is not required
if `concepticon` is ran within the root of the `concepticon-data` clone but might be helpful
if you're working with multiple clones of Concepticon. In this document we assume that all
commands are executed within the root of the Concepticon clone. If unsure, you can explicitly
specify a path with `concepticon --repos=/PATH/TO/concepticon-data YOURCOMMAND`.

The Concepticon API allows you to automatically link your concept list to the Concepticon. We currently support two different styles, one which exhaustively compares each gloss with each other, and one quick style, which compares only those glosses which have been filtered as similar enough in a first run. The styles also differ slightly in their output. Here is, how you can carry out a linking using the quick style of your list called "input.tsv"
```shell
concepticon map_concepts input.tsv
# or 
concepticon map_concepts input.tsv > automatic.tsv  # redirect output to file.
```
This script requires that the Concepticon API has been installed, and that your input list contains at least two columns: one labeled "ID" and one labeled "GLOSS" or "ENGLISH" (for detailed instructions, see the [beginner's guide](https://calc.hypotheses.org/2225)).

The mapping procedure will output another list, containing three additional columns: `CONCEPTICON_ID`, `CONCEPTICON_GLOSS`, and `SIMILARITY` (the latter ranks similarity on a scale between 1 and 5, with 1 being most similar, if there is a matching concept). If there are multiple possibilities of the same similarity, these are output in ranked order, preceded by the `<<<` and followed by `>>>`. Left-overs are marked by three question marks (`???`). The last line also contains the percentage of mapped items with score <= 3, which gives you an idea on how much work still needs to be done to manually refine the mapping.

An excerpt of an example output is here:

```shell
ID	GLOSS	CONCEPTICON_ID	CONCEPTICON_GLOSS	SIMILARITY
1	hair	1040	HAIR	2
2	head	1256	HEAD	2
3	mouth	674	MOUTH	2
4	nose	1221	NOSE	2
...
122	I	1209	I	1
123	thou	1215	THOU	2
124	he	1211	HE	2
125	die 	1494	DIE	2
126	we excl.		???	
<<<			
127	you	1213	YOU	2
127	you	2312	YOU (OBLIQUE CASE OF YOU)	2
>>>			
128	they	817	THEY	2
#	123	128	0.96
```

## Testing 

After you have added your new concept list, you should test whether the mapping and the format 
conforms to our standards (see the checklist below). This can be done by running:

```shell
concepticon test
```

The output will tell you whether your mapping has succeeded and any issues will be reported.
If you run into problems, just let us know, and we try to help as best as we can.


## Checklist for pull requests

If you write a pull request to Concepticon, make sure that you have added the relevant information in the following files:

1. Have you correctly linked your concept list? If so, you should have a linked concept list with minimally the following columns: "ID" (use the form ```FirstAuthorLastName-Year-NumberOfItems-ID``` to create the ID for you concept list and add a disambiguation a/b/c if neccessary), "NUMBER" (a digit, usually following the number in the source, or reflecting the order in the source), "ENGLISH" (if the concept list offers an official English translation) or otherwise "GLOSS" (which requires an additional column indicating the original language of the list), "CONCEPTICON_GLOSS" (the gloss as given in Concepticon), and "CONCEPTICON_ID" (our Concepticon ID).
2. Have you added the metadata for your concept list? You find more information by looking into the file [```conceptlists.tsv```](https://github.com/concepticon/concepticon-data/blob/master/concepticondata/conceptlists.tsv), please contact us if you run in trouble.
3. Have you added your reference for the concept list, and all references which you used in your description, to our bibtex file [```references.bib```](https://github.com/concepticon/concepticon-data/blob/master/concepticondata/references/references.bib)?
4. Have you added new concept sets including proper definitions to our Concepticon in the file [```concepticon.tsv```](https://github.com/concepticon/concepticon-data/blob/master/concepticondata/concepticon.tsv)? If so, have you opened an issue first?
5. Do you reference a source file in PDF, in your description of the concept list in [```conceptlists.tsv```](https://github.com/concepticon/concepticon-data/blob/master/concepticondata/conceptlists.tsv)? If so, send it to @chrzyki in the form of ```FirstAuthorLastNameYear.pdf``` and refer to the respective pull request. Please fill in the respective metadata colum in [```conceptlists.tsv```](https://github.com/concepticon/concepticon-data/blob/master/concepticondata/conceptlists.tsv) with the ```FirstAuthorLastNameYear``` key.
6. Do you have to thank a person for help with the concept list? If you are contributing and not part of our core editorial team, we will add you, so please provide us with your name and affiliation. To keep track of whom to thank, please edit the [```CONTRIBUTORS.MD```](https://github.com/concepticon/concepticon-data/blob/master/CONTRIBUTORS.md) document.
7. Have you tested your modifications by typing ```concepticon test``` in the command line?

In brief, whenever you add a new concept list, you could use the following check-list:

* [ ] concept linking properly done?
* [ ] metadata in ```concepticondata/conceptlists.tsv``` edited?
* [ ] references in ```concepticondata/references/references.bib``` added?
* [ ] new concept sets discussed in issue and added?
* [ ] mentioned source file PDF to @chrzyki?
* [ ] thanked and acknowledged contributors?
* [ ] tested the code? (`concepticon test`)

When you open a pull request (PR) there will be a template where you can mark what applies
to your PR and you can provide additional information. Additionally, please ask one of
the [active editors](CONTRIBUTORS.md) to moderate the PR. The moderator then will decide how to
classify the pull request and assign reviewers accordingly. Depending on the nature and the amount
of changes in a PR (e.g. from minor corrections to new lists and substantial data changes), a
certain number of reviewers will be assigned to review the PR.

## Conventions

We have certain conventions on how to deal with problems when linking concepts to the Concepticon. You can read all about the ups and downs of concept mapping in these blogposts: https://calc.hypotheses.org/1820 and https://calc.hypotheses.org/1844. Here, we currently list them without specific order of preference.

### Missing translations

Missing translations are indicated as NAN, as an example see the list by [Pallas-1786-442.tsv](https://github.com/concepticon/concepticon-data/blob/master/concepticondata/conceptlists/Pallas-1786-442.tsv).

### Missing Concept Sets

If we don't find a concept set for a concept and deem the concept to be too specific to be further mapped, we leave the field empty. All these concept sets are later assigned to a class of concept sets called `<NA>`.

### N-N Mappings

We do NOT allow to carry out N-N mappings between concepts in a concept lists and concept sets in the Concepticon. As a work-around, however, we allow to multiply a respective concept in a given source and assign it to two different concept sets. This has been done, for example, in the list [Matisoff-1978-200](https://github.com/concepticon/concepticon-data/blob/master/concepticondata/conceptlists/Matisoff-1978-200.tsv#L31), where the concept "vagina or breast/milk" clearly indicates that the author means two distinct entries, but lists them in the same line of the list. Similarly, one may encounter that people make a further distinction within a word list, by adding in brackets if, for example, there are actually two words for "frog" in some varieties, a "big frog" and a "small frog". In these cases it is also important to split the respective entry, as it has been done in the list by [List-2016-180](https://github.com/concepticon/concepticon-data/blob/master/concepticondata/conceptlists/List-2016-180.tsv#L8), although, admittedly, the actual decision was already done in the compilation of the concept list. 
