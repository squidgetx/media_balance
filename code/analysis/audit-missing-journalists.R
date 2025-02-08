source(here::here('code/setup.R'))
datadir <- "data/masterdata2"
all.articles <- read_tsv(here(datadir, "articles.tsv"))
all.sources <- read_tsv(here(datadir, "sources.tsv"))
sources <- all.sources %>% filter(policy_label_gpt)
articles <- all.articles %>% filter(policy_label_gpt)

articles.with.author <- articles %>% filter(!is.na(author_name))
articles.with.author %>% nrow

table(!is.na(articles.with.author$edu.undergrad)) %>% prop.table()
table(!is.na(articles.with.author$age_est)) %>% prop.table()

j_covars <- c('edu.undergrad', 'edu.field', 'edu.grad_year', 'exp.year_start', 'gender', 'race.nonwhite')