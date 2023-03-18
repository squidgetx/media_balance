library(tidyverse)


group_articles <- function() {
    files <- list.files("../nyt-metadata")
    dfs <- lapply(files, function(fname) read_tsv(paste0("../nyt-metadata/", fname)))
    df <- do.call("rbind", dfs)

    oped_df <- df %>% filter(section_name == "Opinion", type_of_material == "Op-Ed")

    authors_2020 <- opeds %>%
        filter(pub_date < as.Date("2021-01-01"), pub_date > as.Date("2020-01-01")) %>%
        group_by(authors) %>%
        summarize(n = n(), web_url = last(web_url))
    write_csv(authors_2020, "oped_authors_2020.csv")
}

group_authors <- function() {
    author_desc <- read_csv("authors.csv")
    author_descs <- author_desc %>%
        group_by(author_name) %>%
        summarize(author_descs = paste0(author_desc, collapse = "|"), web_url = first(web_url))
    write_csv(author_descs, "authors_clean.csv")
}

extract_twitter_handles <- function() {
    authors <- read_csv("opeds/authors_clean.csv")
    authors$twitter_handle <- str_extract(authors$author_descs, "@[\\w]*")
    write_csv(authors, "authors_clean.csv")
}