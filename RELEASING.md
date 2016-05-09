
Releasing concepticon-data
==========================

We try to follow a [semantic versioning](http://semver.org/) scheme for releases of
concepticon-data.

Creating a release comprises the following tasks:

1. Make sure all changes are pushed and merged into the `master` branch.
2. Make sure all tests pass.
3. Make sure the data in `master` can be imported into the web app `clld/concepticon`.
4. Make sure all tests pass for the web app.
5. Draft a release 
   - using the correct version number, e.g. `v1.1.0` (don't forget the `v` 
     prefix, since otherwise ZENODO will not pick up the release). 
   - using `CLLD Concepticon 1.0.0` as the title
   - and giving the citation as release description:

> List, Johann-Mattis & Cysouw, Michael & Forkel, Robert (eds.) 2016. Concepticon. 
> A Resource for the Linking of Concept Lists. 
> Jena: Max Planck Institute for the Science of Human History.
> Available online at http://concepticon.clld.org

6. After a while, check on https://zenodo.org for the DOI assigned to the release
   - complete the metadata for the release on ZENODO and
   - add the DOI badge to the release description on GitHub.
7. Create a [new milestone](https://github.com/clld/concepticon-data/milestones) to
   link to issues for the next version.
