default: sources.clean.tsv

sources.clean.tsv: sources.raw.tsv 
	Rscript clean.R

sources.raw.tsv: extracted_to_tsv.py sources.raw.json
	python extracted_to_tsv.py sources.raw.json

sources.raw.json: extract-sources-v3.py ../../../data/articles/relevant.metadata.clean.tsv
	python extract-sources-v3.py ../../../data/articles/relevant.metadata.clean.tsv > sources.raw.json
