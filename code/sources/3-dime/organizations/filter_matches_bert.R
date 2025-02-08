source(here::here('code/setup.R'))

# R code to take the maybe matches from stg0 with the BERT predictions
# divide them into confident matches and still undecided
# We continue to use the 800 entry training set
# to determine these thresholds

# Input is here("code/sources/3-dime/organizations/maybes.ts.stg0.bert.tsv")
# and outputs are maybes.stg1.bert.tsv and matches.stg1.bert.tsv

# Evaluate the performance of the sentence transformer labels
st <- read_tsv(
    here("code/sources/3-dime/organizations/labels.bert.tsv")
) %>%
    filter(
        label %in% c("F", "T")
    ) %>%
    mutate(
        label = as.factor(label == "T")
    )

r <- roc(predictor = st$sim, response = st$label)
# AUC 0.92 is pretty good honestly
r
plot(r)

f1s <- c()
recalls <- c()
precs <- c()
ts <- seq(0.01, 0.99, 0.01)
for (t in ts) {
    st$sim.class <- as.factor(st$sim > t)
    cm <- confusionMatrix(
        data = st$sim.class,
        reference = st$label,
        positive = "TRUE",
        mode = "prec_recall"
    )
    f1 <- cm$byClass["Precision"]
    f1s <- c(f1s, cm$byClass["F1"])
    recalls <- c(recalls, cm$byClass["Recall"])
    precs <- c(precs, cm$byClass["Precision"])
}
perf.df <- data.frame(f1 = f1s, recall = recalls, precision = precs, t = ts)
perf.df %>%
    pivot_longer(c(f1, recall, precision)) %>%
    ggplot(aes(x = t, y = value, color = name)) +
    geom_smooth(se = F) + 
    geom_point()

f1.thresh <- perf.df %>%
    arrange(desc(f1)) %>%
    head(1) %>%
    .$t
best.f1 <- perf.df %>%
    arrange(desc(f1)) %>%
    head(1) %>%
    .$f1
recall.thresh <- perf.df %>%
    filter(round(recall, 2) >= 0.95) %>%
    arrange(desc(t)) %>%
    head(1) %>%
    .$t
prec.thresh <- perf.df %>%
    filter(round(precision, 2) >= 0.95) %>%
    arrange(t) %>%
    head(1) %>%
    .$t

recall.thresh
prec.thresh
best.f1

# Would be awesome to get the F1 over 0.8...

matches.st <- read_tsv(
    here("code/sources/3-dime/organizations/maybes.ts.stg0.bert.tsv")
) %>% mutate(
    sim.class = cut(sim, c(-1, recall.thresh, prec.thresh, 1), labels = c("No", "Maybe", "Match")),
    sim.class.bin = as.factor(sim > f1.thresh)
) %>% distinct(
    organization, name, .keep_all=T
)
matches.st %>% write_tsv(
    here('code/sources/3-dime/organizations/matches.bert.stg1.tsv')
)
matches.st$sim.class %>% table()
matches.st %>% filter(sim.class == 'Maybe') %>% write_tsv(
    here('code/sources/3-dime/organizations/maybes.bert.stg1.tsv')
)

st$sim.class.bin <- as.factor(st$sim > f1.thresh)
confusionMatrix(st$sim.class.bin, st$label, positive='TRUE', mode='prec_recall')

