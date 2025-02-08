source(here::here('code/setup.R'))

library(gender)
library(wru)

# Get the gender of each journalist using the 'gender' package
# First use the first_name provided by linked in
# if this fails, use the first name that we guess naively by splitting the
# journalist name by whitespace
df <- readRDS(here("code/journalists/authors.raw.rds"))
gender.impute.df <- gender(df$first_name) %>% 
    unique() %>% 
    select(name, gender)
df.g <- df %>% 
    left_join(gender.impute.df, by=c('first_name'='name')) %>%
    mutate(
        gender = coalesce(gender.x, gender.y)
    )

df.race <- df.g %>%
    predict_race(surname.only=T) %>% 
    mutate(
        race.missing = (round(pred.bla, digits=6) == 0.215476),
        pred.race.pr = pmax(pred.whi, pred.bla, pred.his, pred.asi, pred.oth),
        pred.race = case_when(
            pred.whi == pred.race.pr ~ 'white',
            pred.his == pred.race.pr ~ 'hispanic',
            pred.bla == pred.race.pr ~ 'black',
            pred.asi == pred.race.pr ~ 'asian',
            pred.oth == pred.race.pr ~ 'other',
            TRUE ~ NA
        )
    )
table(df.race$race.missing, df.race$pred.race, useNA='ifany')
df.race$pred.race %>% table(useNA='ifany')

df.trim <- df.race %>% 
    select(!c(
        gender.x,
        gender.y,
        pred.asi,
        pred.his,
        pred.bla,
        pred.oth,
        pred.whi,
        race.missing
    ))

df.trim %>% as_tibble %>% distinct(clean_name, .keep_all=T) %>% 
    saveRDS(here("code/journalists/authors.gr.rds"))
