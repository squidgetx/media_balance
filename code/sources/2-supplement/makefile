default: sources.supplement.tsv

gov.sources.tsv: prepare.R
	Rscript prepare.R

env.or.ff.tsv: prepare.R
	Rscript prepare.R

gov.sources.cat.tsv: gov.sources.tsv
	python categorize_gov.py

env.or.ff.cat.tsv: env.or.ff.tsv
	python categorize_env_ff.py

politicians.parties.tsv: politicians.tsv
	python categorize_pol_party.py

politicians.tsv: gov.sources.cat.tsv
	Rscript clean.R

sources.supplement.tsv: gov.sources.cat.tsv env.or.ff.cat.tsv politicians.parties.tsv
	Rscript clean.R