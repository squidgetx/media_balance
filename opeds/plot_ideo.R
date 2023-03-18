library(tidyverse)

df <- read_csv("authors_twitter_joined.csv")

hist(df$ideology_normalized)

library(fuzzyjoin)
library(stringi)

opeds <- read_csv("opeds.csv") %>%
    filter(pub_date < as.Date("2021-01-01")) %>%
    fuzzy_left_join(
        df,
        by = c("authors" = "author_name"),
        match_fun = stri_detect_fixed
    )
# imperfect join TODO

opeds %>%
    ggplot(aes(x = pub_date, y = ideology_normalized)) +
    geom_point()

summary(lm(ideology_normalized ~ pub_date, data = opeds))