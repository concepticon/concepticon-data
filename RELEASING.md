
Releasing concepticon-data
==========================

We try to follow a [semantic versioning](http://semver.org/) scheme for releases of
concepticon-data.

Creating a release comprises the following tasks:

- Run [bibtool](http://www.gerd-neugebauer.de/software/TeX/BibTool/en/) on the references 
to normalize them for import:
```
$ bibtool -r concepticondata/references/bibtool.rsc -o concepticondata/references/references.bib concepticondata/references/references.bib
```

- Make sure all changes are pushed and merged into the `master` branch.
- Make sure all tests pass.
- Make sure the data in `master` can be imported into the web app `clld/concepticon`.
- Make sure all tests pass for the web app.
- Draft a release 
  - using the correct version number, e.g. `v1.1.0` (don't forget the `v` 
    prefix, since otherwise ZENODO will not pick up the release). 
  - using `CLLD Concepticon 1.0.0` as the title
  - and giving the citation as release description:

> List, Johann-Mattis & Cysouw, Michael & Forkel, Robert (eds.) 2016. Concepticon. 
> A Resource for the Linking of Concept Lists. 
> Jena: Max Planck Institute for the Science of Human History.
> Available online at http://concepticon.clld.org

- After a while, check on https://zenodo.org for the DOI assigned to the release
  - complete the metadata for the release on ZENODO and
  - add the DOI badge to the release description on GitHub.
- Create a [new milestone](https://github.com/clld/concepticon-data/milestones) to
  link to issues for the next version.


Releasing pyconcepticon
=======================

- Make sure the tests pass
```
nosetests
```

- Bump version number:
  - Change the version number in `setup.py` and commit the change:
```
git commit -a -m"bumped version number"
```

- Create a release tag:
```
git tag -a v0.2 -m"first version to be released on pypi"
```

- Push to github:
```
git push origin
git push --tags
```

- Release to PyPI:
```
python setup.py sdist register upload
```

