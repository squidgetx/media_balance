library(tidyverse)
library(here)
library(caret)

imputed.scores <- read_tsv(here("code/sources/5-impute/test-impute.out.tsv")) %>% select(!c(cfscore))
test.df <- read_tsv(here("code/sources/5-impute/test.impute.tsv")) %>% 
    left_join(imputed.scores) %>%
    filter(!is.na(rank))

# First, correlation between ranks
# Pretty good
ggplot(test.df, aes(x=rank1, y=rank2)) + geom_point() 
cor(test.df$rank1, test.df$rank2)

# Correlation between rank and cfscore
cor(test.df$cfscore, test.df$rank1)
cor(test.df$cfscore, test.df$rank2)
cor(test.df$cfscore, test.df$rank)
# The avg rank is better but not by too much
ggplot(test.df, aes(x=cfscore, y=rank)) + geom_point()  + geom_smooth(method='lm')
table(test.df$rank)

model <- lm(cfscore ~ rank, data=test.df)
test.df$pred.cfscore <- predict(model, test.df)
test.df$resid <- abs(test.df$cfscore - test.df$pred.cfscore)
mean(test.df$resid ^ 2)
# Decent MSE - better than "regular" imputation (MSE 0.45)

# Consider it as a prediction problem
test.df <- test.df %>% mutate(
    true_class = case_when(
        cfscore > 0.22 ~ 'right',
        cfscore < -0.38 ~ 'left',
        TRUE ~ 'center'
    ), 
    impute_class = case_when(
        rank > 1 ~ 'right',
        rank < -1 ~ 'left', 
        TRUE ~ 'center'
    )
)
confusionMatrix(
    reference=test.df$true_class %>% as.factor,
    data=test.df$impute_class %>% as.factor,
    mode='prec_recall'
)

test.df %>% arrange(desc(resid)) %>% select(
    cfscore, pred.cfscore, organization, description, resid
) %>% write_tsv(here('code/sources/5-impute/impute.errs.tsv'))


hist(test.df$resid)
mean(test.df$resid, na.rm=T)
mean(test.df$resid^2, na.rm=T)

agg.df <- test.df %>% group_by(organization, cfscore, cfscore.i, resid) %>% summarize(n=n()) %>% arrange(desc(n))
agg.df %>% filter(resid > 0.5) %>% view

test.df %>% ggplot(aes(x=cfscore, y=resid)) + geom_point()
