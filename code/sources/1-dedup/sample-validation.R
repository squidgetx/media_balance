library(tidyverse)
library(here)
sources <- read_tsv(here("code/sources/1-dedup/sources.deduped.tsv"))


## That did nothing actually, that's a good thing
## Manually check the 100 most common entities?
sources %>%
    group_by(entity_id, category) %>%
    summarize(n = n(), name = first(entity_name), desc = first(entity_desc)) %>%
    arrange(desc(n)) %>%
    head(200) %>%
    write_tsv(here("code/sources/1-dedup/sources.manual.top200.tsv"))
set.seed(1234)
sources %>%
    sample_n(500) %>%
    mutate(category.human = NA) %>%
    select(
        category.human,
        category, entity_name, entity_desc, entity_id
    ) %>%
    write_tsv(here("code/sources/1-dedup/sources.category.validation.500.tsv"))