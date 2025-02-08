source(here::here('code/setup.R'))
df <- read_tsv(here("code/sources/4-comments/sources.comments.clean.tsv"))
df.dime <- df %>%
    group_by(org_id) %>%
    summarize(
        cfscore = first(cfscore),
        desc = first(organization_description),
        category.slant = first(category.slant)
    ) %>%
    filter(!is.na(cfscore))


df.t <- df %>% filter(category %in% c("advocacy", "business"))
set.seed(100)
train <- df.t %>%
    filter(!is.na(cfscore)) %>%
    sample_frac(0.7)
test <- df.t %>%
    filter(!is.na(cfscore)) %>%
    anti_join(train)


model <- lm(cfscore ~ category.slant, data = train)
test.preds <- predict(model, newdata = test)

model <- lm(cfscore ~ category.slant, data = df.t)
df.t$pred.cfscore <- predict(model, newdata = df.t)

summary(model)
paste("Test MSE", mean((test.preds - test$cfscore)^2))
paste("Train MSE", mean((df.t$pred.cfscore - df.t$cfscore)^2, na.rm = T))

df %>%
    left_join(df.t) %>%
    write_tsv(here("code/sources/5-impute/sources.imputed.tsv"))
