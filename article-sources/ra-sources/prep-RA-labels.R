# code to turn the raw TSV of the RA labels to something comparable with chatGPT output

library(tidyverse)
cols <- c("Source", "Hint", "Topic", "Article Name", "Source Type", "Person Name", "Person Title", "Person Category", "Organization Name", "Organization Category", "Organization Subcategory", "Document Title", "Document Type")
eiline_df <- read_tsv("data/RA Labels/Eiline_Abortion.tsv") %>% select(cols)
eiline_df2 <- read_tsv("data/RA Labels/Eiline_Climate.tsv") %>% select(cols)
elin_df <- read_tsv("data/RA Labels/Elin.tsv") %>% select(cols)

df <- rbind(elin_df) %>%
    rename(
        name = "Person Name",
        title = "Person Title",
        `organizational affiliation` = "Organization Name",
        category = "Person Category"
    ) %>%
    filter(`Hint` != "hyperlink")
df %>% write_tsv("RA_labels_clean.tsv")
