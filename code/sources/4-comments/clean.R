source(here::here('code/setup.R'))

df <- read_tsv(here(
    "code/sources/4-comments/sources.comments.tsv"
)
) %>% mutate(
        comment.category = case_when(
            str_detect(comment.category, "Business") ~ "Business",
            str_detect(comment.category, "Environment") ~ "Environment",
            TRUE ~ comment.category
        )
    ) %>%
    select(!c(comment.explanation, cost)) %>%
    rename(
        comment.topic = comment.category
    )
df$comment.topic %>% table()
df %>% write_tsv(
    here(
        "code/sources/4-comments/sources.comments.clean.tsv"
    )
)
