default: balance.html journalists.html analysis.html 

balance.html: balance.Rmd deps
	Rscript -e "rmarkdown::render('balance.Rmd')"

journalists.html: journalists.Rmd deps 
	Rscript -e "rmarkdown::render('journalists.Rmd')"

analysis.html: analysis.Rmd deps
	Rscript -e "rmarkdown::render('analysis.Rmd')"

deps: load.R ../../data/masterdata/sources.tsv

