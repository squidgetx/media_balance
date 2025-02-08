library(tidyverse)
library(here)
args = commandArgs(trailingOnly=TRUE)
articles <- read_tsv(here('code/articles', args[1]))
comments <- read_tsv(here('code/articles/nyt_details/nyt-comments-clean.tsv'))

articles %>% left_join(comments) %>% write_tsv(here('code/articles', args[2]))
