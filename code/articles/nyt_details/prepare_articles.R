library(tidyverse)
library(here)

df <- read_tsv(here('code/articles/articles.clean.policy.tsv'))
df %>% filter(source == 'New York Times') %>% select(
    title, filename, date
) %>% write_tsv(here('code/articles/nyt_details/articles.tsv'))
