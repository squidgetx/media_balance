library(tidyverse)
library(fuzzyjoin)
compare <- function() {
    gpt_sources <- read_tsv("gpt_sources_clean.tsv") %>% mutate(src = "gpt")
    ra_sources <- read_tsv("ra_sources_clean.tsv") %>% mutate(src = "ra")

    ra_sources$filename <- paste0(ra_sources$`Article Name`, ".txt")

    gpt_articles <- unique(gpt_sources$filename)
    ra_articles <- unique(ra_sources$filename)
    common_articles <- intersect(gpt_articles, ra_articles)

    # only validate against data that we have RA data for
    gpt_sources <- gpt_sources %>% filter(filename %in% common_articles)
    ra_sources <- ra_sources %>% filter(filename %in% common_articles)

    gpt_sources$match_name <- gpt_sources$name
    ra_sources$match_name <- ifelse(is.na(ra_sources$name), ra_sources$organization, ra_sources$name)

    merged <- gpt_sources %>% fuzzy_full_join(ra_sources, by = c("filename", "match_name"), match_fun = c(str_equal, str_detect))

    merged$filename <- ifelse(is.na(merged$filename.x), merged$filename.y, merged$filename.x)
    merged.mini <- merged %>%
        select(
            filename,
            `Source Type`,
            src.x,
            src.y,
            name.y,
            title.y,
            organization.y,
            category.y,
            name.x,
            title.x,
            organization.x,
            category.x
        )

    merged.mini %>%
        arrange(filename) %>%
        write_tsv("merged.tsv")

    merged.mini
}

merged.mini <- compare()
# aggregated stats:
agg <- merged.mini %>%
    summarize(
        matched = sum(!is.na(src.x) & !is.na(src.y)),
        gpt_missing = sum(is.na(src.x)),
        gpt_extra = sum(is.na(src.y)),
        total_ra = sum(!is.na(src.y)),
        total_gpt = sum(!is.na(src.x))
    )
agg

agg <- merged.mini %>%
    group_by(filename) %>%
    summarize(
        matched = sum(!is.na(src.x) & !is.na(src.y)),
        gpt_missing = sum(is.na(src.x)),
        gpt_extra = sum(is.na(src.y)),
        total_ra = sum(!is.na(src.y)),
        total_gpt = sum(!is.na(src.x))
    )
