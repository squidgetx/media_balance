source(here::here('code/setup.R'))

matches.agg <- read_tsv(here("code/sources/3-dime/organizations/matches.agg.tsv"))
sources <- read_tsv(here("code/sources/2-supplement/sources.supplement.tsv")) %>% left_join(
    matches.agg
)

matches.agg$entity_id %>% head
sources$entity_id %>% head

is.na(sources$cfscore) %>%
    table() %>%
    prop.table()
table(!is.na(sources$cfscore), sources$category.slant)
# We have dime data for 28% of sources, that's actually pretty good

sources %>% write_tsv(here("code/sources/3-dime/organizations/sources.dime.orgs.tsv"))

# This data includes the academic sources for example
sources %>%
    filter(category.slant == "academic", !is.na(cfscore)) %>%
    group_by(org_id, organization, cfscore) %>%
    summarize(n = n()) %>%
    arrange(desc(n)) %>%
    head(10)


sources$cfscoresd %>% hist()
# Manually review the biggest organizations
sources %>%
    filter(!is.na(organization)) %>%
    filter(category %in% c('advocacy', 'business')) %>%
    group_by(organization, category, org_id, cfscore, cfscoresd) %>%
    summarize(n = n()) %>%
    arrange(desc(n)) %>%
    filter(cfscoresd > 0.5)  %>% 
    head(100)

# TODOS
# Problem: most places have large cfscoresd
