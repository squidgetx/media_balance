default: sources.deduped.tsv

orgs.raw.tsv: ../0-extract/sources.clean.tsv prepare-describe.R
	Rscript prepare-describe.R

orgs.descriptions.tsv: orgs.raw.tsv describe-orgs.py
	python describe-orgs.py

orgs.clustered.tsv: orgs.descriptions.tsv cluster-orgs.R
	Rscript cluster-orgs.R

sources.deduped.tsv: orgs.clustered.tsv clean.R
	Rscript clean.R