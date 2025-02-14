default: sources.dime.orgs.tsv

sources.dime.orgs.tsv: matches.agg.tsv
	Rscript join_matches.R

matches.agg.tsv: maybes.bert.stg1.tsv filter_matches_gpt.R 
	python get-matches-gpt.py
	Rscript filter_matches_gpt.R

maybes.bert.stg1.tsv: maybes.ts.stg0.tsv
	python get-matches-bert.py
	Rscript filter_matches_bert.R

maybes.ts.stg0.tsv: match-candidates.tsv orgs_cleaned.tsv
	Rscript get_matches_ts.R

orgs_cleaned.tsv: prepare_matching.R ../data ../../1-dedup/orgs.clustered.tsv
	Rscript prepare_matching.R


# Depends on 1-dedup/orgs.cleaned.deduped.tsv
# Takes 1.5 hours
#match-candidates.tsv:  prepare_matching.R get-match-candidates.py
#	Rscript prepare_matching.R
#	python get-match-candidates.py  