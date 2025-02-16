default: analysis/_book/index.html

analysis/_book/index.html: ../data/masterdata/sources.tsv
	make -C analysis

../data/masterdata/sources.tsv: sources/sources.tsv journalists/authors.clean.rds articles/articles.clean.tsv clean_all.R
	Rscript clean_all.R

sources/sources.tsv: 
	make -C sources

journalists/authors.clean.rds: 
	make -C journalists

articles/articles.clean.tsv:
	make -C articles

	