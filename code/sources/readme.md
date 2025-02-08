# Source Extraction, Deduplication, and Annotation

This folder contains all code for extracting source data from news article texts and then also cleaning, deduplicating, and then annotating the data with useful supplemental information.

## Source Extraction

Takes the list of article metadata as input and outputs JSON containing the source information.

All intermediate data generated from this code lives mostly in the local directory (`code/sources`). 
Only data that is ready to be used by the final analysis goes to the `data` folder


```
python extract-sources-v3.py ../../data/relevant.metadata.clean.tsv > sources.raw.json
```

Clean the sources and convert them to TSV format (`sources.raw.tsv`)
```
python clean-sources.py sources.raw.json
```

Clean the sources further and prepare the data for deduplication.
People sources are deduplicated within this script.
The code for organization deduplication is more complex, and lives in the `dedup` folder.
```
Rscript clean.R
```

## Organization Deduplication

First, we enrich our dataset by asking GPT to give more information about each organization `python describe-orgs.py`

Second, we use hierarchical clustering to create coarse candidate clusters for deduplication
Finally, we use GPT to adjudicate the clusters.

## Source Supplementation

We further annotate sources with useful information beyond the rough categories assigned by `extract-sources`.

- identify whether government sources are domestic or international
- identify the party affiliation of domestic politicians and bureaucrats where possible 
- identify whether organizations tagged with `advocacy` or `business` are associated with fossil fuels, renewable energy, conservation, other environmental, or other
