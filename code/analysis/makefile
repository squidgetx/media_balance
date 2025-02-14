default: balance.html journalists.html

balance.html: balance.Rmd data/sources.tsv load.R
	Rscript -e "rmarkdown::render('balance.Rmd')"

journalists.html: journalists.Rmd data/sources.tsv load.R
	Rscript -e "rmarkdown::render('journalists.Rmd')"

analysis.html: analysis.Rmd data/sources.tsv
	Rscript -e "rmarkdown::render('analysis.Rmd')"

data/sources.tsv: prep_analysis.R ../sources/sources.tsv
	Rscript prep_analysis.R
