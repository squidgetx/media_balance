default: authors.clean.rds

authors.raw.rds: make_authors.R
	Rscript make_authors.R

authors.gr.rds: authors.raw.rds impute_gender_race.R
	Rscript impute_gender_race.R

authors.patched.rds: authors.gr.rds update_missing.R
	Rscript update_missing.R

authors.edu.rds: authors.patched.rds make_edu_vars.R
	Rscript make_edu_vars.R

authors.clean.rds: authors.edu.rds
	ln -sf authors.edu.rds authors.clean.rds
