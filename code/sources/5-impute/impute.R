source(here::here("code/setup.R"))

df <- read_tsv(here("code/sources/4-comments/sources.comments.clean.tsv"))
orgs <- read_tsv(here("code/sources/5-impute/orgs.imputed.tsv"))

orgs <- orgs %>% select(rank, org_id)
df <- df %>% left_join(orgs)

df %>%
    filter(!is.na(rank)) %>%
    filter(category %in% c("advocacy", "business")) %>%
    group_by(org_id, organization_name, rank) %>%
    summarize(n = n()) %>%
    arrange(desc(n))

# Pretty reasonable

train.df <- read_tsv(here("code/sources/5-impute/test-impute.out.tsv")) %>%
    select(!c(cfscore)) %>%
    left_join(df %>% select(cfscore, org_id) %>% distinct)
get_mse <- function(m) {
    preds <- predict(m, train.df)
    mse <- mean((preds - train.df$cfscore)^2)
    mse
}

print("Train MSE")
feols(cfscore ~ rank, data = train.df) %>% get_mse

model <- feols(cfscore ~ rank, data = train.df)
df$cfscore.i2 <- predict(model, newdata=df)

print("Coverage")
table(!is.na(df$cfscore), !is.na(df$cfscore.i2))
table(!is.na(df$cfscore), !is.na(df$cfscore.i2)) %>% prop.table

df <- df %>% select(!c(
    'organization', 'cids', 'rank', 'organizations', 'titles', 'cluster_id'
)) %>% select(c(
    src_id,
    filename,
    entity_id,
    entity_name,
    entity_desc,

    category,
    category.slant,
    env_category,
    gov_category,

    person_id,
    person_name,
    person_title,
    pol_party,
    document,

    org_id,
    organization_name,
    organization_description,
    organization_raw,

    cfscore.i2,
    cfscore,
    cfscoresd,
    cfscore.median,
    cfscore_src,
    dime.n,

    comments,
    comment.topic,
))

df %>% write_tsv(here('code/sources/5-impute/sources.imputed.tsv'))