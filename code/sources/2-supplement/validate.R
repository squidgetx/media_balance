library(tidyverse)

df <- read_tsv(here("code/sources/2-supplement/sources.supplement.tsv"))
labels <- read_tsv(here("code/sources/2-supplement/validation-env-ff-combined.tsv")) %>% 
    left_join(df, by = c('organization' = "organization_raw"))


## scratch
df <- read_tsv(here('code/sources/2-supplement/env.or.ff.cat.tsv')) %>% filter(
    env_category %in% c('other', 'fossil fuel')
) %>% group_by(env_category) %>% sample_n(50) %>% 
mutate(
    human.label = NA
) %>% select(human.label, name, env_category, desc) %>%
view

