source(here::here('code/setup.R'))

# Clean stage 2 - merge deduped organizations, and set up more detailed categories
# Specifically, use the organization descriptions to identify environmental and fossil fuel groups
# Set up a GPT system to identify bureaucrats and politicians
# Prepare for DIME matching

org.clusters <- read_tsv(here("code/sources/1-dedup/orgs.clustered.tsv"))
sources.stg1 <- read_tsv(here("code/sources/0-extract/sources.clean.tsv"))


sources <- sources.stg1 %>%
    left_join(org.clusters, by = (c("organization", "category.clean"))) %>%
    mutate(
        category.clean = case_when(
            !is.na(cluster.category) ~ cluster.category,
            TRUE ~ category.clean
        ),
        organization = case_when(
            !is.na(organization_name) ~ organization_name,
            TRUE ~ organization
        ),
        category = category.clean,
        org_id = cluster_id
    ) %>%
    select(!c(
        category.clean, cluster.category, n,
        cost.x, cost.y
    )) %>%
    rename(
        organization_raw = organization
    ) %>%
    mutate(
        entity_id = case_when(
            !is.na(org_id) ~ paste0("org-", org_id),
            !is.na(person_id) ~ paste0("person-", person_id),
            TRUE ~ paste0("src-", src_id)
        ),
        entity_name = case_when(
            !is.na(org_id) ~ organization_name,
            !is.na(person_id) ~ person_name,
            TRUE ~ paste(person_title, document)
        ),
        entity_desc = case_when(
            !is.na(org_id) ~ organization_description,
            !is.na(person_id) ~ paste(person_title),
            TRUE ~ NA
        )
    )
sources %>% write_tsv(here("code/sources/1-dedup/sources.deduped.tsv"))

