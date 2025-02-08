library(here)
library(tidyverse)
library(readtext)

articles.all <- read_tsv(here('data/articles/all_articles.metadata.labeled.tsv'))
articles.all$label %>% table
articles.all %>% filter(label == F) %>% select(excerpt) %>% sample_n(10)
articles <- read_tsv(here('data/articles/relevant.metadata.clean.tsv'))
articles %>% filter(batch == 1) %>% select(filename, textfile) %>% write_tsv('data/articles/relevant.metadata.clean.bat1.tsv')
articles %>% filter(batch == 1) %>% sample_n(1) %>% select(filename, textfile) %>% write_tsv('data/articles/relevant.metadata.clean.sample1.tsv')

df.all <- read_tsv(here('data/climate-excerpts/articles/all_articles.metadata.tsv'))
df.all.2 <- read_tsv(here('data/climate-excerpts/articles/metadata.v2.out.tsv'))

colnames(df.all)

colnames(df.all.2)

og_excerpts <- readtext(here(paste0('data/climate-excerpts/articles/excerpts_txt/', df.all$filename, '.txt')), ignore_missing_files = T)
og_excerpts$filename <- str_remove(og_excerpts$doc_id, '.txt')
df.all.exc <- df.all %>% left_join(og_excerpts) %>% rename(excerpt=text)
rbind(df.all.exc, df.all.2)

cols <- intersect(colnames(df.all.exc), colnames(df.all.2))
df.all.12 <- rbind(
    df.all.exc %>% mutate(batch=1) %>% select(all_of(cols)),
    df.all.2 %>% mutate(batch=2) %>% select(all_of(cols))
) %>% mutate(
    excerpt = str_replace_all(excerpt, '[\\s]+', ' ')
)
df.all.12 %>% write_tsv(here('data/articles/all_articles.metadata.tsv'))

df.v1 <- read_tsv(here('data/climate-excerpts/articles/relevant.metadata.tsv')) %>% mutate(
    batch=1
)

df.v2 <- read_tsv(here('data/climate-excerpts/articles/relevant.out.v2.tsv')) %>% mutate(
    batch=2
)


relevant <- rbind(
    df.v1 %>% select(filename, batch) %>% mutate(label=T, cost=NA),
    df.v2 %>% select(filename, cost, label, batch)
)

df.all.relevant <- df.all.12 %>% left_join(relevant) %>% mutate(
    label = replace_na(label, F)
)
df.all.relevant %>% filter(label) %>% select(!c(cost, label, excerpt)) %>% write_tsv(here('data/articles/relevant.metadata.tsv'))
df.all.relevant %>% write_tsv(here('data/articles/all_articles.metadata.labeled.tsv'))

df.all.relevant %>% select(filename, label, cost) %>% write_tsv(
    here('code/articles/topic-labels.tsv')
)

cc <- read_tsv('data/articles/citation-counts.tsv') %>% mutate(
    prop_cite_words = n_cite_words / all_words,
    prop_cite_lines = n_cite_lines / n_lines
)
cc$prop_cite_words %>% hist
cc$prop_cite_lines %>% hist
summary(cc)
