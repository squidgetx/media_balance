source(here::here("code/setup.R"))
# Handle missing journalists
# Logic is a little nasty because we did a few rounds of data collection
# using the "author_normalized" column which only exists at the "article" level

# Do this after gender imputation but before ivy league detection

df <- readRDS(here("code/journalists/authors.gr.rds"))

names <- read_tsv(here("data/articles/relevant.metadata.clean.tsv")) %>%
    mutate(
        clean_name = tolower(author) %>%
            str_remove("^and ") %>%
            str_remove("^-") %>%
            str_split_i(";", 1) %>%
            str_split_i("/", 1)
    ) %>%
    select(clean_name, author_normalized) %>%
    distinct()

missing <- read_csv(here("data/missing journalists/missing_journalists_20241022.csv")) %>%
    select(!c("n", "HY_NOTE", "source")) %>%
    distinct(author_normalized, .keep_all = T)

missing2 <- read_tsv(here("data/missing journalists/manual_authors_01-06-25.tsv")) %>%
    select(!c("n", "race.nonwhite"))

df.m <- df %>%
    left_join(names) %>%
    rows_update(missing, by = "author_normalized") %>%
    rows_update(missing2, by = "clean_name") %>%
    mutate(
        author_name = case_when(
            !is.na(author_normalized) ~ tolower(author_normalized),
            TRUE ~ clean_name
        ),
        author_name = str_remove(author_name, "^by"),
        author_name = str_remove_all(author_name, "for the wall stret journal"),
        author_name = str_remove_all(author_name, "special for usa today"),
        author_name = str_remove_all(author_name, "photos by eve edelheit"),
        author_name = str_remove_all(author_name, "photograph by ashley rodgers"),
        author_name = str_remove_all(author_name, "| photographs by esther horvath"),
        author_name = str_remove_all(author_name, "of the star tribune"),
        author_name = str_remove(author_name, "network"),
        author_name = str_remove(author_name, "usa today"),
        author_name = str_remove(author_name, "and$"),
        author_name = case_when(
            author_name == "(tag bylines with individual items)" ~ NA,
            author_name == "anonymous" ~ NA,
            author_name == "associated press" ~ NA,
            author_name == "baltimore sun" ~ NA,
            author_name == "bloomberg" ~ NA,
            author_name == "bloomberg news" ~ NA,
            author_name == "by by" ~ NA,
            author_name == "city news service" ~ NA,
            author_name == "common sense media" ~ NA,
            author_name == "facebook" ~ NA,
            author_name == "fast company" ~ NA,
            author_name == "fix" ~ NA,
            author_name == "gabriel san román" ~ "gabriel san roman",
            author_name == "georgetown" ~ NA,
            author_name == "healthday" ~ NA,
            author_name == "la times books" ~ NA,
            author_name == "magazine" ~ NA,
            author_name == "michael j de la merced" ~ "michael j. de la merced",
            author_name == "name here" ~ NA,
            author_name == "news" ~ NA,
            author_name == "noted." ~ NA,
            author_name == "of the morning" ~ NA,
            author_name == "reuters" ~ NA,
            author_name == "workborg" ~ NA,
            author_name == "healthday" ~ NA,
            str_starts(author_name, "team") ~ NA,
            str_starts(author_name, "the") ~ NA,
            str_ends(author_name, "staff") ~ NA,
            str_starts(author_name, "from ") ~ NA,
            TRUE ~ author_name
        ),
        author_name = str_trim(author_name),
        author_name = ifelse(author_name == "", NA, author_name),
        # Attempt to normalize
    )

df.a <- df.m %>%
    filter(!is.na(author_name)) %>%
    arrange(edu.grad_year, exp.year_start) %>%
    distinct(author_name, .keep_all = T) %>%
    select(!c(clean_name, n_articles, n_sources, author_normalized, og_name, newspaper))

# Index by clean_name because that's the join key for the article level data
df.all <- df.m %>%
    select(clean_name, author_name) %>%
    distinct() %>%
    left_join(
        df.a
    ) %>%
    mutate(
        # Manually fix this one case
        edu.grad_year = case_when(
            author_name == "Bowerman, Mary" ~ 2012,
            TRUE ~ edu.grad_year
        )
    ) %>% distinct(clean_name, .keep_all=T)

stopifnot(unique(df.all$clean_name) %>% length == nrow(df.all))


df.all %>% saveRDS(here("code/journalists/authors.patched.rds"))
