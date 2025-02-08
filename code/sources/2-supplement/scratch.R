library(tidyverse)
library(here)
validated <- read_tsv(here("code/sources/2-supplement/env.sources.cat.validate.200.labeled.tsv")) %>%
    filter(!is.na(human.label)) %>%
    mutate(
        human.label = case_when(
            human.label == T ~ env_category,
            human.label == F ~ NA,
        )
    )
validated$human.label %>% table()


validated2 <- read_tsv(here("code/sources/2-supplement/hy_env_ff_validation.tsv")) %>% mutate(
    human.label = case_when(
        !is.na(human.label) ~ human.label,
        env_category == "renewable" ~ "environmental",
        TRUE ~ env_category
    )
)
validated2$human.label %>% table()

rbind(
    validated %>% rename(organization = name) %>% select(
        organization, human.label,
    ),
    validated2 %>% select(organization, human.label)
) %>%
    filter(!is.na(organization), !is.na(human.label)) %>%
    distinct() %>%
    write_tsv(here("code/sources/2-supplement/validation-env-ff-combined.tsv"))
