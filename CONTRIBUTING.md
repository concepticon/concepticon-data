# How to Contribute to the CLLD Concepticon?

Contributing to the CLLD Concepticon is simple on the one hand and difficult on the other hand. If you are an experienced user of GitHub and know about the basic ideas behind pull requests and testing in Python, it will be easy to propose changes. Creating the change proposals, however, requires to study the way we encode data in the CLLD Concepticon. Basically, you can propose new concept lists using whatever method you want. We recommend, however, that you have a look at the methods we already created, since these may significantly ease the task of adding new concept lists, or changing the mappings we provide in existing ones.

## GitHub Pull Requests

We won't give you any detailed explanations here but just assume that you find all information you need in this excellent HowTo:

* https://gun.io/blog/how-to-github-fork-branch-and-pull-request

If you experience any problems, just let us know.

## Submitting Concept Lists

Let us assume you have a concept list which you would like to submit to our Concepticon, so that we can afterwards include it and link it. In this case, you could write us an email, but even better, you would file an issue using our [issue tracker](https://github.com/clld/concepticon-data/issues). Here, we collect and classify different kinds of issues. New concept lists are tagged accordingly, and [here](https://github.com/clld/concepticon-data/issues?q=is%3Aissue+is%3Aopen+label%3A%22new+concept+list%22) you can see all concept lists, which we would like to map but have not yet found time to include.

In our workflow, we distinguish different stages of concept list creation and indicate this with tags:

* [scanned](https://github.com/clld/concepticon-data/issues?q=is%3Aissue+is%3Aopen+label%3Ascanned) refers to those concept lists which are already available in a scanned version, so that we can start typing them off. Sometimes, concept lists are only available in some specific archive, and we don't have access to them immediately. In this case, our concept list issue is just tagged as "new concept list", not yet as "scanned".
* [typed](https://github.com/clld/concepticon-data/issues?q=is%3Aissue+is%3Aopen+label%3Atyped) refers to those concept lists which have already been digitized. 
* [formatted](https://github.com/clld/concepticon-data/issues?q=is%3Aissue+is%3Aopen+label%3Aformatted) refers to concept lists which have been already brought into the format needed for mapping, that is, they are given as TSV file, with one field indicating the number, one the concept label, and additional fields indicating additional data as given in the concept list.

Once you filed an issue and provide us with the important information, we will tag the issue accordingly, and try to follow it up. If you have the list in a typed version, or even in a formatted version, you could either directly attach it to your issue, or you could create pull request (see above) where you place your formatted but not yet linked concept list into the folder [unlinked](https://github.com/clld/concepticon-data/tree/master/unlinked).

## Linking Concept Lists

Suppose you have prepared a dataset that contains a concept list and that you would like to submit to the Concepticon, or you have detected a concept list you deem important but which you don't find in our current collection: What are the steps you need to undertake to submit this list to us, and to share it with the whole community? A simple way which is, however, not guaranteed to work immediately, is to write an email or file an issue about a missing concept list. If you do so, we will evaluate the proposal and see what we can do.
Naturally, we'd appreciate it even more if you could provide us with 
* a scanned version of the list, or even better
* a digitized (typed-off) version of the list, or even better
* a linked version of the list.
In all these cases, you could still just write an email or attach the data to the issue, but you could also fork your own version of the concepticon (see "GitHub Pull Requests" above) and officially add the data. 
The advantage of this is that you could be listed as a co-author in the next of the yearly releases of the CLLD Concepticon. We gurantee co-authorship to all authors of **linked versions of new missing concept lists**. We officially thank all people who provided scans and digitized versions on the website at http://clld.concepticon.org.

### Linking Concept Lists: The Manual Style

If you link a concept list manually, we will assume and check automatically and manually that this has been done properly. You can prepare your changes using whatever software you like, be it pure text-files or spreadsheet programs. In order to link a concept list, you need to supply the following information:

* the concept list itself, which should be placed into the folder [conceptlists/](https://github.com/clld/concepticon-data/tree/master/concepticondata/conceptlists). Here, we follow the convention of naming the file according to the schema FirstAuthor-Year-NumberOfItems.tsv. Each list needs to have the following fields (the order is irrelevant):
  - ID: an identifier, following the schema FirstAuthor-Year-NumberOfItems-Number
  - NUMBER: a number or a string that is unique to the given concept
  - ENGLISH or GLOSS: use ENGLISH, if the original language is ENGLISH, use GLOSS, if the original entry of the concept label is another language and the gloss is your translation
  - CONCEPTICON_ID: either a valid id of our Concepticon, or an empty field, if you don't know how to map it (we automatically compute the amount of missing links and badge them for each concept list)
  - CONCEPTICON_GLOSS: the corresponding gloss
  Apart from this, you can add as many further columns as you want. Here, we have further conventions:
  - if you have translations of the gloss in different languages, label them accordingly (CHINESE, FRENCH, etc.)
  - if you have a ranked list, provide the RANK as an integer and name the field RANK
  - there are further "soft" conventions, which you can inspect by having a look at the different concept lists which are already mapped
* the reference, provided as a BibTex entry in the file[references.bib](https://github.com/clld/concepticon-data/blob/master/concepticondata/references/references.bib). Please use the schema FirstAuthorYear and add a, b, c, etc. if there are multiple entires for the same author and the same yere, 
* a description of the basic characteristics of the list in the file [conceptlists.tsv](https://github.com/clld/concepticon-data/blob/master/concepticondata/conceptlists.tsv). Here, we recommend you to either contact us if there are further questions, or to just look up how we usually encode the respective values. Not all information is required, but it is our goal to try always to fill out as many cells for a new concept list as possible. 
* if you have a scan of your list which does not fall under the copyright law (no full books, but pages in which one can see the concept lists should be acceptable), please label it as BibTexKey.pdf and put it in the folder [sources](https://github.com/clld/concepticon-data/tree/master/concepticondata/sources)

If you feel that you need to add new identifiers which are currently missing in the CLLD Concepticon, please contact us, and we will provide you with the relevant information on how to add new concept set identifiers. Please also do not hesitate to ask us if therea are any further questions.

### Using automatic mapping software

We created scripts that make it easy to map new concept lists. These scripts are in the folder [helpers/](https://github.com/clld/concepticon-data/tree/master/helpers). One script is of essential importance here:

* [maplist.py](https://github.com/clld/concepticon-data/blob/master/helpers/maplist.py), a script that takes the path to a concept list as argument.

```shell
$ python maplist.py yourconceptlist
```
This script requires the most recent version of [LingPy](http://lingpy.org). Your concept list should minimally contain one column labelled as "GLOSS" and one column labelled as "NUMBER" (you should change GLOSS later to ENGLISH, in case the original language for concept labels is English). The script produces automatic mappings with multiple solutions from which you can choose. The solutions are graded using a numerical schema from 1 to 8, with one indicating complete identity, and 8 indicating missing entries. 

There are more scripts that can ease the task of mapping concept lists. Please contact us if you have questions, and we gladly tell you how to use them.

## Testing

After you have added your new concept lists, you should test whether the mapping and the format conforms to our standards. For this, we use the [nose](http://pythontesting.net/framework/nose/nose-introduction/) library. To test, if you have nose installed, just type:

```shell
$ nosetests 
```

The output will tell you whether your mapping has succeded. If you run into problems, just let us know, and we try to help as best as we can.
