source(here::here('code/setup.R'))
df <- read_tsv(here("code/sources/4-comments/sources.comments.clean.tsv"))
df.dime <- df %>%
    group_by(org_id, organization_name, category, category.slant) %>%
    summarize(
        cfscore = first(cfscore),
        cfscoresd = first(cfscoresd),
        description = first(organization_description),
        category.slant = first(category.slant)
    ) %>%
    filter(!is.na(cfscore)) 
df.test <- df.dime %>% filter(cfscoresd < 0.3) %>% filter(category %in% c('advocacy', 'business'))
df.test %>% write_tsv(
        here("code/sources/5-impute/test.impute.tsv")
)
df.test %>% head(10) %>% write_tsv(
        here("code/sources/5-impute/test.impute.10.tsv")
)
 
orgs <- df %>%
    group_by(org_id, organization_name, organization_description, category.slant) %>%
    summarize(
        n=n()
    ) %>% rename(
        description = organization_description
    )
orgs %>%
    write_tsv(
        here("code/sources/5-impute/orgs.tsv")
    )
