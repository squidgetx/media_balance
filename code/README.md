# Both Sides Journalism: A Changing Climate

## Abstract

Journalists shape news by selecting sources, guided historically by the balance norm, which emphasizes objectivity and diverse perspectives. However, changes in newsroom revenue models, staff demographics, and Trump's attacks on the media challenge this norm. This paper analyzes how balance norm in journalists' citation patterns has changed in climate change articles across six major U.S. newspapers from 2012 to 2022. Using large language models, we construct a comprehensive dataset of news source citations and measure source level balance based on the categorization and political orientation of cited sources. We show that the share of balanced articles declined dramatically over our time period, from 40\% to less than 33\%. 

A within-journalist analysis shows that a large portion of the change in balance is driven by many existing journalists becoming less likely to produce balanced articles after 2016. We speculate that Trump's presidency spurred editors and journalists to relax their adherence to the balance norm by raising its salience. We also show that the journalists who reduce their production of balanced news most after 2016 are younger, less experienced, and less educated.

## Data

- `masterdata` contains all of the cleaned data files used in the main analysis
    - `articles.tsv`: `textfile` (unique), `date`, `source` (newspaper), `is_policy_label_gpt`, `author_name`, `age_est` (estimated author age at time of publication), and all associated author level information (see below)
    - `authors.tsv`: `author_name`, `n_articles`, `gender`, `race.nonwhite`, `edu.grad_year` (college graduation year), `exp.year_start_journo` (first year of work experience from LinkedIn), `edu.has_postgrad`, `edu.field` (undergrad major), `elite_undergrad_ivyplus` (indicator for Ivy League plus Stanford and MIT), `elite_undergrad_25` (indicator for top 25 selective undergrad)
    - `sources.tsv`: `src_id` (unique), `textfile` (for joining with article level information), `category` (one of 8 major categories), `category.slant` (more detailed category label), `dime.n` (number of matches for this source in DIME), `cfscore.raw` (mean DIME ideology score), `cfscoresd` (SD of ideology scores for matches for this source in DIME), `cfscore.i2` (imputed DIME ideology score), `org_id` (unique organization name), `person_id` (unique person name), `pol_party` (Democrat/Republican label where relevant) 
- `articles` contains the raw text data of the articles in `txt` and `v2/txt` folders as well as raw article level metadata downloaded from Proquest in `all_articles.metadata.tsv`
- `dime` contains the raw downloaded DIME data from Bonica
- `validation labels` contains manual label data collected to validate our methods
- `missing journalists` contains manual journalist level information

## Code

`clean_all.R` collects source, article, and author data from other places in the project, does some final cleaning and variable construction, and outputs the main analysis files into `masterdata`

### Analysis

The `analysis` directory contains all of the code related to the final analysis of the data

- Run `make` to knit all files, or you can just knit the Rmds directly.
- `analysis.Rmd` contains main descriptives and some exploratory analysis
- `balance.Rmd` contains the main results about the trend of balance over time
- `journalists.Rmd` contains the main results about journalist characteristics and balance as the dependent variable
- `load.R` is an R snippet that loads the main data files and contains functions used to construct the balance and ideology scores in the main analysis

### Sources

The `sources` directory contains all code related to extracting sources from the articles and manipulating/categorizing/cleaning them. 

- `0-extract/` contains code related to extracting the sources from the articles
- `1-dedup/` contains code related to deduplicating organization names using hierarchical clustering
- `2-supplement/` contains code related to categorizing organizations using GPT. There is a current known bug wher this step's build needs to run make twice. The first time it will error.
- `3-dime/` contains code related to matching organization names  and politicians to DIME
- `4-comments/` contains code related to classifying the topic of the source citation using GPT
- `5-impute/` contains code related to imputing DIME scores using GPT
- `6-clean/` contains final cleaning code

Each subdirectory contains a `makefile` that performs the main task of the data pipeline and a `README` that goes into further detail as to what's going on. You can also run `make` from the `sources` directory which performs all steps of the data pipeline. The cleaned sources file lives in `sources/sources.tsv`

### Articles

The `articles` directory contains code related to cleaning, categorizing, and analyzing article metadata based on the raw metadata dump from Proquest. You can run the entire article data pipeline using `make`. The cleaned articles are output into `articles.clean.tsv`

Currently, the articles pipeline is **broken**, so running `make` will not really do anything. `articles.clean.tsv` is provided.


- The `count-citations` subdirectory contains simple analysis code describing what proportion of article text is a 3rd party quote. (This should maybe be moved to `analysis` folder)
- The `nyt_details` subdirectory contains code used to scrape the number of comments on NYT articles. 

#### Topic Labeling

The `label-topics` subdirectory contains all code used to label whether an article is about climate policy based on its text using GPT. 

The initial dataset was selected by searching the ProQuest database to find articles that mention climate change. However, many of these are not about climate change. For example, they might be mostly about a candidates' campaign strategy and note that the candidate mentioned climate change once in a speech.

The file `data/articles/all_articles.metadata.tsv` contains an entry for every row in the dataset including the first 250 words of the article in the `excerpts` column.

We use GPT to label whether the article is about climate change or not based on this data (`label-topic.py`).

Then, we use GPT to label whether the article is about climate **policy** or not (`label-topic-policy.py`)

### Journalists

This directory contains code related to both scraping and then cleaning journalist data. You can run the entire pipeline related to cleaning using `make`. The scraping code (in the `scrape` folder) is super messy and may be broken. 


The cleaned journalist data is output to `authors.clean.rds`

### Source Validation

This folder contains code related to setting up a Potato annotation server for crowdworkers to evaluate the quality of our GPT based source extraction method. 

## Dependencies

- R
- Python
    - You can install all Python related dependencies using `pip install -r requirements.txt` from the `code` directory
- You need an OpenAI key to use the GPT API. However, for convenience the cached results are stored in `progress.jsonl` files throughout this replication archive. Re-building the replication archive (eg, using `make`) will by default use these cached files.
