default: politicians/sources.dime.orgs.pols.tsv

politicians/sources.dime.orgs.pols.tsv: organizations/sources.dime.orgs.tsv
	make -C politicians

organizations/sources.dime.orgs.tsv: ../2-supplement/sources.supplement.tsv data
	make -C organizations

data:
	ln -sf ../../../data/dime data