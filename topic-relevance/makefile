default:
	python parse_proquest.py $(data)
	python label-topic.py $(data) > $(data)/labeled.tsv
	Rscript filter_labels.R $(data)/labeled.tsv > $(data)/relevant.tsv
