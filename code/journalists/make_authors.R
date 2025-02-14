source(here::here('code/setup.R'))
library(fuzzyjoin)

title_keywords <- c(
    "writer",
    "report",
    "news",
    "times",
    "post",
    "tribune",
    "usa today",
    "journal",
    "enviro",
    "wildlife",
    "climate",
    "earth",
    "editor",
    "sustain",
    "energy",
    "professor"
)
keyword_re <- paste(title_keywords, collapse = "|")

# Start with the list of journalist names extracted from article metadata
# Assign the "clean_name" object. This logic is also used in
# clean_linkedin.py

og_articles <- read_tsv(here("code/articles/relevant.metadata.clean.tsv"))
og_authors <- og_articles %>%
    filter(!is.na(author)) %>%
    mutate(
        author = tolower(author),
        clean_name = author %>%
            str_remove("^and ") %>%
            str_remove("^-") %>%
            str_split_i(";", 1) %>%
            str_split_i("/", 1)
    ) %>%
    group_by(clean_name) %>%
    summarize(
        n = n(),
        sources = paste(unique(source), collapse = ","),
        n_sources = length(unique(source)),
    )

# Load journalist profiles scraped directly from newspaper websites
bylines <- read_tsv(here("code/journalists/data/bylines.tsv")) %>%
    rename_with(~ paste(., "byline", sep = "."))

# Load journalist information collected using Nubela and Linked in scraping
scrape_df <- read_tsv(here("code/journalists/data/author.data.tsv"))

# Load manual corrections for the scrape data.
# These corrections simply describe bad matches in the scrape data.
# manual_review of 0 or -1 means the data is bad and should be deleted.
# manual_review of 1 or 2 means the data is good and we keep it.
manual <- rbind(
    read_tsv(here("code/journalists/data/manual_authors_03-11-24.tsv")) %>%
        mutate(
            manual_review = replace_na(manual_review, 0)
        ) %>%
        select(clean_name, full_name, manual_review),
    read_tsv(here("code/journalists/data/manual_authors_03-12-24.tsv")) %>%
        filter(!is.na(manual_review)) %>%
        select(clean_name, full_name, manual_review)
) %>% distinct()
scrape_df.clean <- scrape_df %>%
    left_join(manual) %>%
    filter(manual_review > 0 | is.na(manual_review))

authors <- og_authors %>%
    left_join(
        scrape_df.clean
    ) %>%
    rename(n_articles = n) %>%
    mutate(
        summary = str_replace_all(summary, "\n|\t", " "),
        occupation = str_replace_all(occupation, "\n|\t", " "),
        headline = str_replace_all(headline, "\n|\t", " ")
    ) %>% stringdist_left_join(
        bylines, by=c('clean_name'='name.byline')
    )

# Clean up
authors.clean <- authors %>%
    mutate(
        gender = tolower(gender),
        first_name = ifelse(is.na(first_name), str_split_i(clean_name, "\\s", i = 1), first_name),
        surname = ifelse(is.na(last_name), str_split_i(clean_name, "\\s", i = -1), last_name),
        full_name = case_when(
            !is.na(name.byline) ~ name.byline,
            !is.na(full_name) ~ full_name,
            !is.na(mr_name) ~ mr_name,
            TRUE ~ clean_name
        ),
        twitter_url = case_when(
            !is.na(twitter.byline) ~ twitter.byline,
            !is.na(mr_twitter) ~ mr_twitter,
            TRUE ~ tw_url
        ),
        website_url = case_when(
            !is.na(href.byline) ~ href.byline,
            TRUE ~ mr_website
        )
    ) %>%
    select(!c(
        mr_linkedin,
        mr_twitter,
        tw_url,
        last_name,
        mr_error,
        manual_review,
        twitter.byline,
        href.byline,
        mr_website,
        name.byline,
        og_sources,
        mr_name,
    )) %>%
    rename(
        muckrack_url = mr_url,
        linkedin_connections = li_connections,
        email = email.byline,
        newspaper = source.byline,
        location = mr_location
    ) %>%
    relocate(
        c(
            clean_name, sources, full_name, first_name, surname, gender,
            occupation, headline, summary
        )
    )


# Next, load journalist profiles manually corrected by RA
manual3 <- read_csv(here("code/journalists/data/missing_journalists_ra.csv"))
manual4 <- read_csv(here("code/journalists/data/20240602_linkedin_no_edu_sorted.csv")) %>% select(colnames(manual3))
ra.manual <- manual3 %>%
    rbind(manual4) %>%
    mutate(
        edu.grad_year = ifelse(edu.grad_year == "not found", NA, edu.grad_year),
        edu.undergrad = ifelse(edu.undergrad == "not found", NA, edu.undergrad),
        edu.field = ifelse(edu.field == "not found", NA, edu.field),
        exp.year_start_journo = ifelse(exp.year_start_journo == "not found", NA, exp.year_start_journo),
        exp.year_start = ifelse(exp.year_start == "not found", NA, exp.year_start),
        manual_review = is.na(edu.field) & is.na(edu.undergrad) & is.na(edu.field) & is.na(exp.year_start) & is.na(exp.year_start_journo),
        manual_review = as.numeric(!manual_review)
    ) %>%
    filter(manual_review == 1) %>%
    mutate(
        edu.grad_year = ifelse(edu.grad_year == "did not graduate", NA, as.numeric(edu.grad_year)),
        exp.year_start_journo = as.numeric(exp.year_start_journo),
        exp.year_start = as.numeric(exp.year_start)
    ) %>%
    select(!c(`Note`, "manual_review")) %>%
    distinct(clean_name, sources, .keep_all = T)

authors.corrected <- authors.clean %>% rows_update(ra.manual, by = c("clean_name", "sources"), unmatched = "ignore")

authors.corrected%>% saveRDS(here("code/journalists/authors.raw.rds"))
