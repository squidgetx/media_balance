sources.tsv: 6-clean/sources.adjust.tsv
	ln -sf 6-clean/sources.adjust.tsv sources.tsv

6-clean/sources.adjust.tsv: 5-impute/sources.imputed.tsv
	make -C 6-clean

5-impute/sources.imputed.tsv: 4-comments/sources.comments.clean.tsv
	make -C 5-impute

4-comments/sources.comments.clean.tsv: 3-dime/politicians/sources.dime.orgs.pols.tsv
	make -C 4-comments

3-dime/politicians/sources.dime.orgs.pols.tsv: 2-supplement/sources.supplement.tsv
	make -C 3-dime

2-supplement/sources.supplement.tsv: 1-dedup/sources.deduped.tsv
	make -C 2-supplement

1-dedup/sources.deduped.tsv: 0-extract/sources.clean.tsv
	make -C 1-dedup

0-extract/sources.clean.tsv: 
	make -C 0-extract