sources.adjust.tsv: sources.clean.tsv adjust.R
	Rscript adjust.R

sources.clean.tsv: dedup-pols.R ../5-impute/sources.imputed.tsv
	Rscript dedup-pols.R