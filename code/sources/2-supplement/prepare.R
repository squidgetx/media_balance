source(here::here('code/setup.R'))

sources <- read_tsv(here("code/sources/1-dedup/sources.deduped.tsv"))

# Split data into gov sources and advocacy/business 

gov <- sources %>%
    filter(category == "government") %>%
    group_by(entity_id) %>%
    summarize(n = n(), entity_name = first(entity_name), entity_desc = first(entity_desc))

gov %>%
    write_tsv(here("code/sources/2-supplement/gov.sources.tsv"))

eff <- sources %>%
    filter(category == "advocacy" | category == "business") %>%
    group_by(entity_id) %>%
    summarize(name = first(entity_name), desc = first(entity_desc)) 
eff %>%
    write_tsv(here("code/sources/2-supplement/env.or.ff.tsv"))

