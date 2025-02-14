source(here::here('code/setup.R'))

dime <- read_csv(here("data/dime/dime_contributor_pac.csv")) %>%
    mutate(contributor_name = str_trim(gsub("[[:punct:] ]+", " ", contributor_name))) %>%
    group_by(contributor_name) %>%
    summarize(
        cfscore = mean(contributorcfscore),
        cfscoresd = sd(contributorcfscore),
        cids = paste(bonicacid, collapse = ",")
    )
dime %>% write_tsv(here("code/sources/3-dime/organizations/dime_contributor_pac_clean.tsv"))

orgs <- read_tsv(here("code/sources/1-dedup/sources.deduped.tsv")) %>%
    filter(!is.na(organization_name)) %>%
    mutate(
        contributor_name = tolower(organization_name)
    ) %>%
    select(entity_id, contributor_name) %>%
    distinct()
orgs %>%
    write_tsv(
        here("code/sources/3-dime/organizations/orgs_cleaned.tsv")
    )
