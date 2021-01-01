# gij bent

Scripts for the gij bent paper. Anthe Sevenants (2021-01-01).

## sort-corpus.py

This is the script which turns the Twitter corpus into my own corpus. You need Python 3 to run the script.
Numerous packages need to be installed in order to be able to run the script. I advise to use virtual
environments to not clutter your Python package repository. This means (on Linux):
1. Create virtual environment: `python3 -m venv venv`
2. Enable virtual environment: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`

All XML files from the corpus files need to be placed in a folder "tweets" (premade in the archive).
There should be 1467 XML files in that folder, originating from both corpus archives.

Run script: `python3 sort-corpus.py`

You can exit the virtual environment with `deactivate`.

## dedupe.py

Removes duplicates from the generated corpora. `python3 dedupe.py`
Paths are hardcoded to the corpus/ directory so the generated corpora need to be there.

## gij-bent.R

The R script containing all statistical analyses. Required packages are mentioned inside the R script.
The R script loads `corpus_shared.csv` from the root directory. You need to combine `corpus/corpus_zijt.csv`
and `corpus/corpus_bent.csv` manually. A precombined and manually corrected (see paper) final corpus
is already supplied as `corpus_shared.csv` in the root folder.