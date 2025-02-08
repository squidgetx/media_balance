source(here::here('code/setup.R'))

# R code to use text similarity measures to identify potential match candidates 
# Calculates multiple measures (cosine, jaccard, etc) then uses 
# a logistic regression to give a total match score between 0 and 1
# We use training data labels.tsv of 800 expert coded entries
# to train the regression

# Outputs 4 files: 
# -- matches.ts.stg0.tsv are pairs that we are confident match or don't 
# -- maybes.ts.stg0.tsv are pairs that we are unsure about
# -- bert_training_textsim.pos.tsv are positive cases from matches.ts.stg0.tsv, 
#    used to train a future BERT model
# -- bert_training_textsim.neg.tsv is a random negative sample from matches.ts.stg0.tsv, 
#    to train a future BERT model

match.candidates <- read_tsv(here("code/sources/3-dime/organizations/match-candidates.tsv")) %>% 
    left_join(
        read_tsv(here("code/sources/3-dime/organizations/dime_contributor_pac_clean.tsv")) %>% mutate(
            dime_id = row_number() - 1
        )
    )
orgs <- read_tsv(here("code/sources/3-dime/organizations/orgs_cleaned.tsv")) %>%
    mutate(
        org_row_num = row_number() - 1
    ) %>%
    filter(!is.na(contributor_name)) %>%
    rename(organization = contributor_name)


matches <- match.candidates %>%
    mutate(
        org_row_num = as.integer(row_number() / 100)
    ) %>%
    inner_join(orgs)

labels <- read_tsv(
    here("code/sources/3-dime/data/labels.tsv")
) %>% rename(name = contributor_name, organization = org)

corpus <- fedmatch::build_corpus(c(matches$name, labels$name), unique(c(matches$organization, labels$organization)))
matches <- matches %>%
    mutate(
        wgt_jac_dist = 1 - wgt_jaccard_distance(name, organization, corpus, nthreads = 4),
        jw_sim = stringdist::stringsim(name, organization, method = "jw", p = 0.1),
        cosine_sim = stringdist::stringsim(name, organization, method = "cosine"),
    )

labels <- labels %>% mutate(
    wgt_jac_dist = 1 - wgt_jaccard_distance(name, organization, corpus, nthreads = 4),
    jw_sim = stringdist::stringsim(name, organization, method = "jw", p = 0.1),
    cosine_sim = stringdist::stringsim(name, organization, method = "cosine"),
)

bin.labels <- labels %>% filter(label %in% c("F", "T"))
# Split data into training (70%) and testing (30%) sets
set.seed(123)
trainIndex <- createDataPartition(bin.labels$label, p = 0.7, list = FALSE)
trainData <- bin.labels[trainIndex, ]
testData <- bin.labels[-trainIndex, ]
train_control <- trainControl(method = "cv", number = 5)

# Train logistic regression model using the three similarity measures
logistic_model <- train(
    label ~ wgt_jac_dist + jw_sim + cosine_sim,
    data = trainData,
    method = "glm",
    family = "binomial",
    trControl = train_control
)
predictions <- predict(logistic_model, newdata = testData, type = "prob")[, 2]
roc(predictor = predictions, response = testData$label == "T")

precision_positive <- c()
for (thresh in seq(0, 1, 0.01)) {
    cmat <- confusionMatrix(
        as.factor(predictions > thresh),
        (testData$label == "T") %>% as.factor(),
        positive = "TRUE",
        mode = "prec_recall"
    )
    precision_positive <- c(precision_positive, cmat$byClass["Precision"])
}
pdf <- data.frame(th = seq(0, 1, 0.01), r = precision_positive)
pdf %>% ggplot(aes(x = th, y = r)) +
    geom_point()
positive_threshold <- pdf %>%
    filter(r > 0.95) %>%
    .$th %>%
    min()
# 0.79
positive_threshold

precision_negative <- c()
for (thresh in seq(0, 1, 0.01)) {
    cmat <- confusionMatrix(
        as.factor(predictions < thresh),
        (testData$label == "F") %>% as.factor(),
        positive = "TRUE",
        mode = "prec_recall"
    )
    precision_negative <- c(precision_negative, cmat$byClass["Precision"])
}
ndf <- data.frame(th = seq(0, 1, 0.01), r = precision_negative)
ndf %>% ggplot(aes(x = th, y = r)) +
    geom_point()
negative_threshold <- ndf %>%
    filter(r > 0.95) %>%
    .$th %>%
    max()
testData$pred <- predictions
testData %>%
    filter(label == "T") %>%
    arrange(pred) %>%
    head() %>%
    kable()


logistic_model_full <- train(
    label ~ wgt_jac_dist + jw_sim + cosine_sim,
    data = bin.labels,
    method = "glm",
    family = "binomial",
    trControl = train_control
)
prob_predictions <- predict(logistic_model_full, newdata = matches, type = "prob")[, 2]
prob_predictions %>% hist(main = "Distribution of predicted match probability")
matches$pred <- prob_predictions

matches <- matches %>% mutate(
    ts.sim.class = cut(pred, c(0, negative_threshold, positive_threshold, 1), labels = c(
        "No",
        "Maybe", "Match"
    ))
)
matches$ts.sim.class %>% table
matches %>% write_tsv(
    here("code/sources/3-dime/organizations/matches.ts.stg0.tsv")
)

matches %>%
    filter(pred > negative_threshold & pred < positive_threshold) %>%
    select(
        name, organization
    ) %>%
    sample_frac(1) %>%
    write_tsv(
        here("code/sources/3-dime/organizations/maybes.ts.stg0.tsv")
    )

matches %>%
    filter(pred > positive_threshold) %>%
    write_tsv(
        here("code/sources/3-dime/organizations/bert_training_textsim.pos.tsv")
    )

matches %>%
    filter(pred < negative_threshold) %>%
    sample_n(10000) %>%
    write_tsv(
        here("code/sources/3-dime/organizations/bert_training_textsim.neg.tsv")
    )

# 90k maybe options
