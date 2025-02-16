# Do all final pre-analysis cleaning and joining
# Writes data to the masterdata folder

source(here::here("code/setup.R"))
library(rlang)
datadir <- "data/masterdata"

sources <- read_tsv(here("code/sources/sources.tsv"))

articles <- read_tsv(here("code/articles/articles.clean.tsv"))

authors <- readRDS(here("code/journalists/authors.clean.rds")) %>% filter(!is.na(author_name))

articles.authors <- articles %>%
    mutate(
        clean_name = tolower(author) %>%
            str_remove("^and ") %>%
            str_remove("^-") %>%
            str_split_i(";", 1) %>%
            str_split_i("/", 1)
    ) %>%
    left_join(authors, by = c("clean_name")) %>%
    mutate(
        ## Article level data
        year = year(date),
        year.q = quarter(date, with_year = T),
        post2016 = year > 2016,
        admin = case_when(
            year < 2016 ~ 'Obama',
            year < 2020 ~ 'Trump',
            TRUE ~ 'Biden'
        )),
        newspaper_lean = case_when(
            str_detect(source, "Wall St") ~ "RIGHT",
            str_detect(source, "New York") ~ "LEFT",
            str_detect(source, "Washington") ~ "LEFT",
            str_detect(source, "Los Angeles") ~ "LEFT",
            str_detect(source, "Chicago Tribune") ~ NA,
            str_detect(source, "USA Today") ~ NA,
        ),

        ## Journalist level data - varies by article because it uses year
        is_career = exp.year_start_journo == exp.year_start,
        years_nonj = exp.year_start_journo - exp.year_start,
        field.journo = str_detect(tolower(edu.field), "journal|comm|media"),
        field.political = str_detect(tolower(edu.field), "political|gov"),
        race.nonwhite = pred.race != "white",
        age_est_2017 = case_when(
            !is.na(edu.grad_year) ~ 2017 - edu.grad_year + 22,
            !is.na(exp.year_start) ~ 2017 - exp.year_start + 22,
            TRUE ~ NA
        ),
        age_est = year - 2017 + age_est_2017,
    ) %>%
    mutate_if(is_character, \(x) str_remove_all(x, "[\r\n\t]"))


sources.articles.authors <- sources %>%
    left_join(articles.authors) %>%
    filter(!is.na(filename))

articles.clean <- sources.articles.authors %>%
    group_by(filename) %>%
    summarize(
        n_srcs = n(),
        n_unique_src_types = length(unique(category)),
    ) %>%
    left_join(articles.authors)

author_columns <- c("author_name", intersect(colnames(authors), colnames(articles.authors)))
authors.clean <- sources.articles.authors %>%
    group_by(author_name) %>%
    summarize(n_articles=n()) %>%
    left_join(articles.authors %>% select(all_of(author_columns))) %>%
    distinct(author_name, .keep_all = T)

sources.articles.authors %>%
    write_tsv(here(datadir, "sources.tsv"))
articles.clean %>% write_tsv(here(datadir, "articles.tsv"))
authors.clean %>% write_tsv(here(datadir, "authors.tsv"))

# Write orgs separately as well for auditing purposes
orgs <- sources %>%
    group_by(org_id, organization_name, organization_description, cfscore, cfscore.i2) %>%
    summarize(
        n = n(),
    )
orgs %>% write_tsv(here(datadir, "organizations.tsv"))
