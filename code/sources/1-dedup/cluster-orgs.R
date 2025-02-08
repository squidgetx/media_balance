source(here::here('code/setup.R'))
library(fastcluster)
library(quanteda)
library(quanteda.textstats)

df.all <- read_tsv(here("code/sources/1-dedup/orgs.descriptions.tsv")) %>% mutate(
    block = case_when(
        category.clean %in% c("advocacy", "business", "media", "citizen", "other") ~ "A",
        category.clean %in% c("government", "international", "academic") ~ "B",
        TRUE ~ category.clean
    )
)
table(df.all$block)
# organization is the original organization name from the old data
# organization_name is the name given by GPT
# organization_description is the desription given by GPT

df <- df.all %>% filter(block == 'A')
cluster_subdf <- function(text) {
    tic()

    corp <- corpus(text)
    toks <- tokens(corp, remove_punct = T, remove_symbols = T)
    dfmat <- toks %>%
        dfm(tolower=T) %>%
        dfm_remove(stopwords('en'))
    dist <- as.dist(1 - textstat_simil(dfmat, method='cosine'))
    clust <- hclust(dist, method = "ward.D2")
    toc()

    clust
}

cluster_block <- function(b, h) {
    df <- df.all %>% filter(block == b)
    proper_nouns <- df$organization_description %>%
        str_extract_all("\\b[A-Z0-9][^\\s]*\\b") %>%
        sapply(\(x) paste0(x, collapse=' '))
    df$text <- paste(df$organization, df$organization_name, proper_nouns)
    clust <- cluster_subdf(df$text)
    df$cluster <- cutree(clust, h = h)
    df
}

proper_nouns <- df.all$organization_description %>%
    str_extract_all("\\b[A-Z0-9][^\\s]*\\b") %>%
    sapply(\(x) paste0(x, collapse=' '))
df.all$text <- paste(df.all$organization, df.all$organization_name, proper_nouns)
clust <- cluster_subdf(df.all)
df.all$cluster_id <- cutree(clust, h = 0.3)

# Process in blocks to ease the computational burden
# About 1 min
df.A <- cluster_block("A", h=0.2)
df.B <- cluster_block("B", h=0.2)
df.clust <- rbind(df.A, df.B) %>% mutate(
    cluster_id = paste0(block, "-", cluster)
) 
df.clustered <- df.clust %>% group_by(cluster_id) %>% summarize(
    cluster.n=n(),
    cluster.text = paste0(text, collapse=', '),
) 
metacluster <- cluster_subdf(df.clustered$cluster.text)
df.clustered$metacluster <- cutree(metacluster, h=0.3)
df.clust <- df.clust %>% left_join(df.clustered)
df.clust$cluster_id <- df.clust$metacluster
df.clust <- df.clust %>% group_by(
    cluster_id
) %>% mutate(
    organization_name = fmode(organization_name),
    organization_description = fmode(organization_description),
    cluster.category = fmode(category.clean),
    cluster.n = n()
)
df.clust.final %>% colnames
df.clust.final <- df.clust %>% select(!c('cluster', 'metacluster', 'block', 'cluster.text', 'persons', 'cluster.n', 'text'))
df.clust.final %>% write_tsv(here('code/sources/1-dedup/orgs.clustered.tsv'))

df.clust.final %>% distinct(category.clean, organization)
nrow(df.clust.final)


# Print details
df.clust %>%
    group_by(cluster_id) %>%
    summarize(n = n()) %>%
    .$n %>%
    table()
df.clust %>%
    group_by(cluster_id) %>%
    mutate(n = n()) %>%
    filter(n > 10) %>%
    arrange(desc(n), cluster_id) %>%
    select(organization, n, cluster_id, text) %>%
    view()

# Test cases
check_same_cluster <- function(df, org_name) {
    df %>%
        filter(str_detect(organization, org_name)) %>%
        .$cluster_id %>% unique %>% length == 1
}
check_same_cluster(df.clust, 'taylor shellfish')
check_same_cluster(df.clust, 'birthstrike')
check_same_cluster(df.clust, 'goldman sachs group')

