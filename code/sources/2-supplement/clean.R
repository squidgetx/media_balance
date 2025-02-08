source(here::here('code/setup.R'))

# Validate and clean the environment and political labels

df <- read_tsv(here("code/sources/2-supplement/gov.sources.cat.tsv"))

if (F) {
    set.seed(1234)
    df %>%
        mutate(human.label = NA) %>%
        select(human.label, entity_name, gov_category, entity_desc, entity_id) %>%
        sample_n(200) %>%
        write_tsv(
            here("code/sources/2-supplement/gov.sources.cat.validate.200.tsv")
        )
} else {
    validated <- read_tsv(here("code/sources/2-supplement/gov.sources.cat.validate.200.labeled.tsv"))
    n <- validated %>%
        filter(!is.na(human.label)) %>%
        nrow()
    binom.test(sum(validated$human.label, na.rm = T), n)
    # >96% acc
}

df.gov.clean <- df %>% mutate(
    gov_category = case_when(
        gov_category %in% c("US bureaucrat", "US politician", "Non-US") ~ gov_category,
        str_detect(gov_category, "Intergovernmental") ~ "international",
        str_detect(gov_category, "US") ~ NA,
        TRUE ~ "Non-US"
    )
)
df.gov.clean$gov_category %>% table()

df <- read_tsv(here("code/sources/2-supplement/env.or.ff.cat.tsv"))

if (F) {
    set.seed(1234)
    df %>%
        mutate(human.label = NA) %>%
        select(human.label, name, env_category, desc, entity_id) %>%
        sample_n(200) %>%
        write_tsv(
            here("code/sources/2-supplement/env.sources.cat.validate.200.tsv")
        )
} else {
    validated <- read_tsv(here("code/sources/2-supplement/env.sources.cat.validate.200.labeled.tsv"))
    n <- validated %>%
        filter(!is.na(human.label)) %>%
        nrow()
    binom.test(sum(validated$human.label, na.rm = T), n)
    # >94% acc
}

df.env.clean <- df %>% mutate(
    env_category = case_when(
        str_detect(env_category, "fossil") ~ "fossil fuel",
        str_detect(env_category, "enviro") ~ "environmental",
        str_detect(env_category, "renewable") ~ "renewable",
        TRUE ~ NA
    )
)
df.env.clean$env_category %>% table(useNA = "ifany")

sources <- read_tsv(here("code/sources/1-dedup/sources.deduped.tsv")) %>%
    left_join(df.gov.clean %>% select(entity_id, gov_category)) %>%
    left_join(df.env.clean %>% select(entity_id, env_category)) %>%
    mutate(
        category.slant = case_when(
            !is.na(env_category) ~ env_category,
            !is.na(gov_category) ~ gov_category,
            TRUE ~ category
        )
    )
sources$category.slant %>% table()

sources
# This looks like a good categorization!

# Write out sources for politicians
sources %>%
    filter(category.slant == "US politician") %>%
    group_by(person_name) %>%
    summarize(
        titles = paste(unique(person_title), collapse = ","),
        organizations = paste(unique(organization_name), collapse = ",")
    ) %>%
    filter(!is.na(person_name)) %>%
    write_tsv(here("code/sources/2-supplement/politicians.tsv"))

sources.suppl <- sources %>%
    left_join(
        read_tsv(here("code/sources/2-supplement/politicians.parties.tsv")) %>% select(!c(cost)) %>% filter(!is.na(person_name))
    ) %>%
    mutate(
        pol_party = case_when(
            str_detect(pol_party, "Democrat") ~ "Democrat",
            str_detect(pol_party, "Republican") ~ "Republican",
            !is.na(pol_party) ~ "Other",
            TRUE ~ NA
        )
    )
sources.suppl %>% write_tsv(
    here("code/sources/2-supplement/sources.supplement.tsv")
)
sources.suppl$pol_party %>% table()
