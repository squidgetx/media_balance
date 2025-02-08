default:
	Rscript preprocess.R
	python make_pol_states.py
	Rscript check_matches.R

full:
	Rscript preprocess.R
	python match-pols-rapidfuzz.py
	python make_pol_states.py
	Rscript check_matches.R