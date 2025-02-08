# Code to dedup people
# This is basically not dependent on any of the other major steps
library(fastcluster)
source(here::here('code/setup.R'))

sources <- read_tsv(here("code/sources/5-impute/sources.imputed.tsv"))

ppl <- sources %>%
    filter(!is.na(person_name)) %>%
    group_by(person_name, category) %>%
    summarize(
        titles = paste0(unique(person_title), collapse = ", "),
        organizations = paste0(unique(organization_name), collapse = ", "),
        pol_party = fmode(pol_party),
        n = n()
    ) %>%
    mutate(
        nametext = paste(rep(person_name, n), collapse = " "),
        poltext = ifelse(is.na(pol_party), "", paste(rep(pol_party, floor(sqrt(n)), collapse = " "))),
        text = paste(nametext, titles, organizations, pol_party, poltext, category) %>% str_remove_all("NA"),
        block = case_when(
            category %in% c("government", "international", "other") ~ "a",
            category %in% c("academic", "advocacy") ~ "b",
            category %in% c("business", "citizen", "media") ~ "c",
        )
    )

cluster_subdf <- function(text) {
    corp <- corpus(text)
    toks <- tokens(corp, remove_punct = T, remove_symbols = T)
    dfmat <- toks %>%
        dfm(tolower = T) %>%
        dfm_remove(stopwords("en")) %>%
        dfm_tfidf()
    dist <- as.dist(1 - textstat_simil(dfmat, method = "cosine"))
    clust <- hclust(dist, method = "ward.D2")
    clust
}

cluster_block <- function(df, h) {
    clust <- cluster_subdf(df$text)
    df$cluster <- cutree(clust, h = h)
    df
}

cluster_all <- function(ppl) {
    print("Clustering person names...  this usually takes a minute or two")
    tic()
    df.a <- cluster_block(ppl %>% filter(block == "a"), h = 0.3)
    df.b <- cluster_block(ppl %>% filter(block == "b"), h = 0.2)
    df.c <- cluster_block(ppl %>% filter(block == "c"), h = 0.15)
    toc()
    df.clustered <- rbind(df.a, df.b, df.c) %>% mutate(
        cluster_id = paste0(block, "-", cluster)
    )
    df.clustered
}

df.clustered <- cluster_all(ppl)
length(unique(df.clustered$cluster_id)) / nrow(df.clustered)


# Get the original names and categories with the attached
# cluster id
names <- df.clustered %>%
    select(cluster_id, person_name, category) %>%
    filter(!is.na(person_name)) %>%
    distinct()

# Add the person_id field to the original dataset
# Find the modal name, title, and category
sources.p <- sources %>% left_join(names) %>% mutate(
    person_id = cluster_id
) %>% select(!c(cluster_id)) %>% rename(
    src_name = person_name,
    src_title = person_title,
    src_org = organization_raw,
    src_document = document,
    src_summary = comments,
    src_topic = comment.topic,
) %>% group_by(person_id) %>% mutate(
    person_name = ifelse(is.na(person_id), NA, fmode(src_name)),
    person_category = ifelse(is.na(person_id), NA, fmode(category)),
    person_title = ifelse(is.na(person_id), NA, fmode(src_title)),
) %>% select(!c(entity_id, entity_name, entity_desc))

# Person category is only useful when we can use it to get rid of "other"
# designiations I think ?

sources.p %>% filter(person_category != category) %>% select(
    person_name,
    organization_name,
    person_category,
    category,
) %>% nrow() 
# Around 1k sources where person_category does not match the given category
# For now I think we leave it alone. Most of these are reasonable edge cases
# where academics and advocacy mix, kind of. 
# Also a very small proportion of sources (<1%)

# Rename and reorder columns
sources.pr <- sources.p %>% select(
    filename,

    src_id,
    src_name,
    src_title,
    src_org,
    src_summary,
    src_topic,

    category,
    category.slant,
    env_category,
    gov_category,

    cfscore,
    cfscore.median,
    cfscoresd,
    cfscore_src,
    dime.n,
    cfscore.i2,

    person_id,
    person_name,
    pol_party,

    org_id,
    organization_name,
    organization_description,
)

sources.pr %>% write_tsv(here('code/sources/6-clean/sources.clean.tsv'))

