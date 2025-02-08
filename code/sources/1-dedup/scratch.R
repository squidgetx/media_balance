library(tidyverse)
library(here)

orgs <- read_tsv('code/sources/1-dedup/orgs.raw.tsv')
descs <- read_tsv('code/sources/1-dedup/orgs.descriptions.tsv')

sources <- read_tsv(here('code/sources/0-extract/sources.clean.tsv')) %>% filter(
    !is.na(organization)
)

orgs.agg <- sources %>% group_by(organization, category) %>% 
    summarize(
        n=n(),
        persons = paste(head(unique(person_name), 5), collapse=','),
        n.category.clean = length(unique(category.clean)),
        category.clean = head(unique(category.clean))
    ) %>% left_join(descs, by=c('organization', 'category')) %>% 
    mutate(
        n=n.x,
        persons=persons.x
    )

descs2 <- orgs.agg %>% group_by(
    organization, n, category.clean
) %>% summarize(
    organization_description = first(organization_description),
    organization_name = first(organization_name),
    persons = first(persons),
    cost = first(cost)
)
descs2$organization_description %>% is.na %>% table
descs$organization_description %>% is.na %>% table
colnames(descs)
colnames(descs2)

descs2 %>% write_tsv(
   'code/sources/1-dedup/orgs.descriptions.tsv' 
)

colnames(descs)


descs %>% left_join(orgs)

descs %>% left_join(orgs) %>% write_tsv(
here('code/sources/dedup/orgs.descriptions.tsv')
)
# Possible abbreviations
orgs %>% filter(str_length(organization) < 6)
orgs %>% filter(str_count(organization, "\\.") > 2 & str_length(organization) < 20) %>% head(50) %>% kable

