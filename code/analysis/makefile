default: _book/index.html

_book/index.html: deps 01-descriptives.Rmd 02-balance.Rmd 03-journalists.Rmd 04-validate.Rmd
	Rscript -e "bookdown::render_book('index.Rmd')"

deps: load.R ../../data/masterdata/sources.tsv

