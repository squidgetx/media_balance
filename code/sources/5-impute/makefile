default: sources.imputed.tsv

orgs.imputed.tsv: impute-pairwise.py orgs.tsv
	python impute-pairwise.py orgs.tsv orgs.imputed.tsv

sources.imputed.tsv: orgs.imputed.tsv impute.R
	Rscript impute.R