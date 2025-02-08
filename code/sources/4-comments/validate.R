library(tidyverse)
library(here)

df <- read_tsv(here('code/sources/4-comments/sources.comments.clean.tsv'))
df %>% group_by(comment.topic) %>% sample_n(10) %>% select(comment.topic, comments) %>% view
df %>% group_by(organization_name, cfscore) %>% summarize(n=n()) %>% arrange(desc(n)) %>% select(
    organization_name, cfscore, n) %>% head(20)
