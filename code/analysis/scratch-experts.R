library(tidyverse)
library(here)
datadir <- 'data/masterdata'
sources <- read_tsv(here(datadir, "sources.tsv"))
sources$category %>% table()
s1 <- sources %>% group_by(year) %>% summarize(
    n_acad = sum(category == 'Academic'),
    prop_acad = n_acad/n()
)
s1 %>% ggplot(aes(x=year, y=prop_acad)) + geom_line()

s2 <- sources %>% filter(is_policy_article) %>% group_by(year) %>% summarize(
    n_acad = sum(category == 'Academic'),
    prop_acad = n_acad/n()
)
s2 %>% filter(year > 2012) %>% ggplot(aes(x=year, y=prop_acad)) + geom_line() + geom_point()

s3 <- sources %>% filter(is_policy_article) %>% 
    group_by(year, source) %>% summarize(
    n_acad = sum(category == 'Academic'),
    prop_acad = n_acad/n()
)
s3 %>% filter(year > 2012) %>% 
    ggplot(aes(x=year, y=prop_acad, color=source, lty=source)) + geom_line() +
    theme_bw()
ggsave(here('figures/academics_over_time.png'), width=6, height=4)


