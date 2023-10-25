# gij bent

Scripts for the article 'Zijt gij dat of bent gij dat?' -- Een alternantiestudie van de tweede persoon enkelvoud van zijn in Vlaamse tussentaal.

This repository houses all the scripts that were used for the analysis in my article on *gij bent* in Dutch. There are three general components:

1. **Tweet retrieval and sorting.** This was done in Python using [snscrape](https://github.com/JustAnotherArchivist/snscrape). Unfortunately, the library no longer works for Twitter, so you won't be able to replicate my output. All files pertaining to this process are in the root directory.
2. **Statistical analysis.** This was done in R. All files for the analysis can be found in the `analysis/` directory.
3. **Article.** The Quarto document with the reporting can be found in the `paper/` directory. It uses files from `analysis/`.

## Tweet retrieval and sorting

All `.py` files in the root directory are used for the tweet retrieval and sorting process.

1. `1-retrieve-tweets.py`: used to query Twitter. Output is written to jsonl files in `output/`. Now defunct.
2. `2-sort-tweets.py`: used to create a TSV dataset from the jsonl files. Outputs to TSV.
3. `3-geoguess.py`: used to attach geolocation to every tweet. Outputs to a separate geo information dataset.
4. `4-gender-detect.py`: used to guess the gender of tweet authors. Outputs to a separate gender information dataset.
5. `5-correct.py`: used to find incorrectly retrieved tweets. Outputs a meta information dataset.
6. `6-merge.py`: used to merge all datasets together and filter wrong tweets. Outputs a final dataset.

## Statistical analysis

All `.R` files in the root directory are used for statistical analysis. All files are made to work in the report, except for `gij-bent-gam2.R`.

- `geo-map.R`: prints a map of Flanders. Embedded in the report.
- `gij-bent2.R`: loads the dataset. Embedded in the report.
- `kloeke.R`: prints a map of the Low Countries with forms for 'you are' in dialect. Embedded in the report.
- `gij-bent-gam2.R`: prints the map of *gij bent*. *Not* embedded in the report, since it takes a solid four minutes to generate the map. This means you need to generate the image first, which is then used in the report.

## Article

I wrote the article in [Quarto](https://quarto.org/). The idea of Quarto is that you write your paper once, which you can then export to HTML, Word and PDF. The paper is generated dynamically, and all regression analyses, graphs and numbers are included on the fly. It uses the files from `analysis/`.

## Reproducibility

As of now, I am unsure how I can distribute the dataset with tweets, since they contain personal information. You can also no longer generate the dataset yourself, since the Twitter scraper is now defunct. I am trying to think of a solution. If you are interested in the meantime, send me an email.