# diff-algebra

Use changesets as vectors in a codespace


## Problem

We would like to estimate the coverage on a "target" revision using the coverage information from some later "covered" revision. This should be possible by mapping the coverage backward, from the "covered" to the "target" using the sequence of changesets between.

Furthermore, tests run at Firefox-scale have coverage variability because of environmental variability; which can include time of day, operating system latency, ordering of network responses, an many more.  Running a test will not likely get you the full coverage for the test, rather some subset. Multiple runs are required; and the results unioned 

Even more: Coverage tests are very expensive to run; requiring 200 machines, and generating about 20gigs of data per run. Running coverage on every changeset is not an option, nevermind multiple times to get a stable coverage number.

## A solution        

Treat coverage coverage as a vector, with changesets as (matrix) transforms, and use matrix multiplication to translate what little coverage we do have to all the other changesets; both forward and backward in time.

## A better solution?

Instead of operating on coverage vectors, we could perform some pre-calculation: For a seed revision we can give every code line a transcendentally unique ID (TID), which is unique over all revisions; past, present and future. We can then use the same algebra to map the TIDs to a subsequent revision; giving us the ability to track "lines" moving inside the files. The adjacent revisions will have TID gaps: caused by net-new lines; which must be assigned TIDs also. The changeset mapping continues to cover as many revisions we need; assigning a TID to every `(revision, file, line)` tuple.

With every revision, every file, and every line given a TID, we can map coverage easier: When we collect coverage on a revision we can convert `(coverage_revision, file, line)` to `TID`, and then lookup `TID` for the target `(target_revision, file, line)`. This can be used to project coverage deep into the past and future quickly. It can be used to merge coverage from multiple coverage runs over different revisions, and it allows us to know the coverage on any revision.

### Problems

The Firefox codebase is 2million lines of code, with about 300 changes made per day. Given a year of history, we would expect a database of TIDs to contain about 200billion `(coverage_revision, file, line, TID)` tuples. We will require a low-latency service that can provide this information, and a centralized server that is responsible for assigning TIDs to the net-new lines.

### How can this fail?

If a source file has added decision code, then a function may no longer be called. Past coverage mapped forward may wrongly conclude a function is covered. Similarly, removed decision code may make future coverage mapped to the past wrongly conclude a function is covered. There are probably other pathologies like this.

## Challenge

Build a web service, or code APi, that
 
* accepts `(revision, file)` and returns all lines with their TIDs.
* accepts `(revision, file, lines)` and returns the TIDs for just the lines given


## Requirements

* ElasticSearch 1.7.x (a very old version) - used to hold repository info 



