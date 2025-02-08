default: analysis.html

analysis.html: analysis.Rmd data/sources.tsv
	Rscript -e "rmarkdown::render('analysis.Rmd')"

data/sources.tsv: prep_analysis.R ../sources/sources.tsv
	Rscript prep_analysis.R
