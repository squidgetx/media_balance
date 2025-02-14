default: articles.clean.comments.tsv
	ln -sf articles.clean.comments.tsv articles.clean.tsv

articles.clean.comments.tsv: articles.clean.policy.tsv nyt_details/nyt-comments-clean.tsv merge_comments.R 
	Rscript merge_comments.R articles.clean.policy.tsv articles.clean.comments.tsv

# TODO : Fix this, somehow we lost the cache :(

# articles.clean.policy.tsv: relevant.metadata.clean.tsv
#	 python label-topic-policy.py relevant.metadata.clean.tsv articles.clean.policy.tsv

# Joins the topic labels with the original set of labels 
# Outputs only the articles about policy
# relevant.metadata.clean.tsv: topic-labels.tsv clean.R
#	Rscript clean.R

# topic-labels.tsv: all_articles.metadata.tsv
# 	python label-topic.py ./all_articles.metadata.tsv

### Validation related tasks ###

validate.html: policy-labels-validation.tsv validate.Rmd
	Rscript -e "rmarkdown::render('validate.Rmd')"

policy-labels-validation.tsv: label-topic-policy.py
	python topic-policy.py relevancy_validation_sample.tsv policy-labels-validation.tsv
