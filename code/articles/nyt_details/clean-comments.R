library(tidyverse)
library(here)

df <- read_csv(here('code/articles/nyt_details/nyt-comments.tsv'))

df <- df %>% mutate(
    n_comments = case_when(
        str_detect(n_comments, 'K') ~ as.numeric(str_replace(n_comments, 'K', '')) * 1000,
        TRUE ~ as.numeric(n_comments)
    )
) %>% rename(
    web_url = `_pkey`
)

articles <- read_tsv(here('code/articles/nyt_details/articles-with-urls.tsv'))

articles %>% left_join(df) %>% write_tsv(here('code/articles/nyt_details/nyt-comments-clean.tsv'))
