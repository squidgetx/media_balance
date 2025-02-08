source(here::here('code/setup.R'))

# We have the names of the cited organizations and the rough categorization
# But we still need to do a lot of deduplicating because GPT is very
# inconsistent with how it spells/words organization names
# eg, "WWF" vs "world wildlife foundation"

# This file takes the sources and identifies potentially unique organizations 
# that we will then bring back to GPT to get longer descriptions of
# in order to power the deduplication process.

sources <- read_tsv(here('code/sources/0-extract/sources.clean.tsv')) %>% filter(
    !is.na(organization)
)

orgs.agg <- sources %>% group_by(organization, category.clean) %>% 
    summarize(
        n=n(),
        persons = paste(head(unique(person_name), 5), collapse=','),
    )

orgs.agg %>% write_tsv(
    here('code/sources/1-dedup/orgs.raw.tsv')
)

