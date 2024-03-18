
# Releasing concepticon-data

We try to follow a [semantic versioning](http://semver.org/) scheme for releases of
concepticon-data.

Creating a release comprises the following tasks:

- Check the list of not linked concepts - with new concept sets some of these could
  be ticked off!
  ```shell script
  concepticon notlinked
  ```

- Run [bibtool](http://www.gerd-neugebauer.de/software/TeX/BibTool/en/) on the references
to normalize them for import:
  ```shell
  bibtool -r concepticondata/references/bibtool.rsc -o concepticondata/references/references.bib concepticondata/references/references.bib
  ```

- Recreate network data in concept lists (optionally also download raw data again):
  ```shell
  concepticon recreate_networks
  ```

- Recreate the statistics pages:
  ```shell
  concepticon stats
  ```

- Recreate and push the linking data:
  ```shell
  concepticon make_linkdata
  ```
- Check and/or update `metadata.json` (which is read via
  `clldutils.apilib.API.dataset_metadata`)

- Afterwards, recreate `.zenodo.json`:
  ```shell
  concepticon citation --version vX.Y.Z
  ```

- Verify that `.zenodo.json` contains the (potentially) updated information from
  `metadata.json`

- Make sure all changes are pushed and merged into the `master` branch.
- Make sure all tests pass, and also address warnings about missing PDFs (see [handling source PDFs](#upload_sources))
  ```shell
  concepticon test
  ```

- Make sure CLDF-creation works:
  ```shell
  cldfbench makecldf cldfbench_concepticon.py --glottolog-version v5.0
  ```

- Adapt `CHANGELOG.md`

- Commit the updates for this version and push updated data:
  ```shell
  git commit -a -m"<version> release"
  git tag -a v<version> -m"release <version>"
  git push origin
  git push origin --tags
  ```

- Draft a release via GitHub UI
  - picking the correct tag, e.g. `v1.1.0`
  - using `CLLD Concepticon <version>` as the title
  - and giving the citation obtained running `concepticon citation` as release description.

- After a while, check on https://zenodo.org for the DOI assigned to the release
  - complete the metadata for the release on ZENODO and
  - add the DOI badge to the release description on GitHub.
- Create a [new milestone](https://github.com/concepticon/concepticon-data/milestones) to
  link to issues for the next version.

- Create the corresponding CLDF dataset release following the instructions
  at https://github.com/concepticon/concepticon-cldf/blob/master/RELEASING.md

- Tweet


<a name="upload_sources"> </a>
## Handling source PDFs

Source PDFs for concept lists - like all binary or media content of CLLD databases - are
uploaded to [CDSTAR](https://cdstar.eva.mpg.de). This is done by

1. running
   ```shell
   concepticon upload_sources
   ```
2. deleting the uploaded PDF files from `concepticondata/sources`
3. commiting and pushing the changes in concepticon/concepticon-data
4. commiting and pushing the changes in the global media catalog in clld/meta

