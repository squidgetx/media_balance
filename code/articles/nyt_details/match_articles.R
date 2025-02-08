library(tidyverse)
library(here)
library(fedmatch)

nyt <- read_tsv(here("code/articles/nyt_details/nyt_archive.tsv")) %>%
    mutate(
        year = as.Date(pub_date) %>% year(),
        month = as.Date(pub_date) %>% month(),
        headline = clean_strings(headline),
        print_headline = clean_strings(print_headline),
        ym = paste0(year, "-", month)
    ) %>%
    distinct(nyt_id, .keep_all = T)
articles <- read_tsv(here("code/articles/nyt_details/articles.tsv")) %>% mutate(
    year = as.Date(date) %>% year(),
    month = as.Date(date) %>% month(),
    ym = paste0(year, "-", month),
    title = clean_strings(title),
)
# We have 10K NYT articles we want to find the URLs of
# We have 756K NYT articles we have the metadata for

articles10 <- articles %>% sample_n(10)

match_headlines <- function(df) {
    match_result <- fedmatch::merge_plus(
        df,
        nyt,
        by.x = "title",
        by.y = "print_headline",
        unique_key_1 = "filename",
        unique_key_2 = "nyt_id",
        multivar_settings = build_multivar_settings(
            blocks = "ym",
            compare_type = "stringdist",
            wgts = c(1),
            threshold = 0.95
        ),
        match_type = "multivar",
    )

    df.unmatched <- df %>% filter(!(filename %in% match_result$matches$filename))

    match_result2 <- fedmatch::merge_plus(
        df.unmatched,
        nyt,
        by.x = "title",
        by.y = "headline",
        unique_key_1 = "filename",
        unique_key_2 = "nyt_id",
        multivar_settings = build_multivar_settings(
            blocks = "ym",
            compare_type = "stringdist",
            wgts = c(1),
            threshold = 0.95
        ),
        match_type = "multivar",
    )

    all.matches <- rbind(match_result$matches, match_result2$matches) %>% distinct(
        nyt_id, filename, .keep_all = T
    )
    all.matches
}
system.time(match_headlines(articles %>% sample_n(10))) # 3.5s
system.time(match_headlines(articles %>% sample_n(100))) # 12s
system.time(match_headlines(articles %>% sample_n(400))) # 40s
system.time(match_headlines(articles %>% sample_n(1000))) 
system.time(
    matches <- match_headlines(articles)
)

urls <- matches %>% group_by(filename) %>% summarize(
    web_url = first(web_url, na.rm=T)
) 
nrow(urls) 
nrow(articles)
nrow(urls)  / nrow(articles)
# 85% of articles have a web URL. That's not bad!
urls %>% write_tsv(here('code/articles/nyt_details/articles-with-urls.tsv'))

saveRDS(matches, "nyt_matches.RDS")
# why are there more matches than nonmatches
