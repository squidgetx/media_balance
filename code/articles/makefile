default: articles.clean.comments.tsv
	ln -sf articles.clean.comments.tsv ../../data/articles/articles.clean.tsv

articles.clean.comments.tsv: articles.clean.policy.tsv nyt_details/nyt-comments-clean.tsv merge_comments.R 
	Rscript merge_comments.R articles.clean.policy.tsv articles.clean.comments.tsv

articles.clean.policy.tsv: relevant.metadata.clean.tsv
	python label-topic-policy.py relevant.metadata.clean.tsv articles.clean.policy.tsv

relevant.metadata.clean.tsv: topic-labels.tsv
	Rscript clean.R

topic-labels.tsv:
	python label-topic.py ../../data/articles/all_articles.metadata.tsv

validate.html: policy-labels-validation.tsv validate.Rmd
	Rscript -e "rmarkdown::render('validate.Rmd')"

policy-labels-validation.tsv: label-topic-policy.py
	python label-topic-policy.py ../../data/articles/relevancy_validation_sample.tsv policy-labels-validation.tsv