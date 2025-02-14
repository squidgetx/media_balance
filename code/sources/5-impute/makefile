default: sources.imputed.tsv

orgs.imputed.tsv: impute-pairwise.py orgs.tsv
	python impute-pairwise.py orgs.tsv orgs.imputed.tsv

sources.imputed.tsv: orgs.imputed.tsv impute.R
	Rscript impute.R

orgs.tsv: prepare.R ../4-comments/sources.comments.clean.tsv
	Rscript prepare.R