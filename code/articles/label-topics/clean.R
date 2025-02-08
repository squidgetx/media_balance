library(tidyverse)
library(here)
library(stringr)

# First, assign the topic labels to the main dataset

df <- read_tsv(here('data/articles/all_articles.metadata.tsv'))
labels <- read_tsv(here('code/articles/topic-labels.tsv'))

df.rel <- df %>% left_join(labels)
df.rel %>% write_tsv(here('code/articles/all_articles.metadata.labeled.tsv'))

df.v0 <- df.rel %>% filter(label) %>% mutate(
    source = case_when(
        str_detect(source, "New York") ~ "New York Times",
        str_detect(source, "Wall") ~ "Wall Street Journal",
        str_detect(source, "Washington") ~ "Washington Post",
        str_detect(source, "Los Angeles") ~ "Los Angeles Times",
        str_detect(source, "Chicago") ~ "Chicago Tribune",
        str_detect(source, "USA") ~ "USA Today",
    )
) %>% filter(!is.na(source))


df.v0 %>% ggplot(aes(x=date, color=source)) + geom_bar(stat='count')

# Investigate weird spikes in the data
df.v0 %>% group_by(date, source) %>% summarise(n=n()) %>% arrange(desc(n))
# the washington post has a suspiciously large number of articles published on new years day 2013-2015
df.v0 %>% filter(source == 'Washington Post' & date == '2013-01-01')
# many titles with the date in the title, extract with regex and assign the correct date 
df.v0.1 <- df.v0 %>% mutate(
    posted_date = str_extract(title, "\\(Posted\\s([0-9-]+\\s[0-9:]+)\\)") %>%
        str_remove_all("\\(Posted\\s|\\s[0-9:]+\\)") %>% 
        as.Date(),
    date = case_when(
        is.na(posted_date) ~ date,
        TRUE ~ posted_date
    ), 
    title = str_remove_all(title, "\\(Posted\\s([0-9-]+\\s[0-9:]+)\\)")
)

# Remove duplicate articles
# Gather same source, author, title articles
dup.candidates <- df.v0.1 %>% group_by(source, author, title) %>% 
    mutate(daterange = max(date) - min(date), n=n(), rn=row_number()) %>% 
    filter(n > 1) 
# Many of these are legit repeat titles from eg, weekly columns
# Drop the ones that occur within a 6 day window
dups <- dup.candidates %>% filter(daterange <= 6) %>% 
    arrange(title) %>% select(author, title, rn, date, filename)
df.v0.2 <- df.v0.1 %>% left_join(dups) %>% filter(is.na(rn) | rn == 1) %>% 
    select(!c(rn, posted_date))

# Set correct filename paths
df.v0.2 <- df.v0.2 %>% mutate(textfile = case_when(
    batch==1 ~ paste0('txt/', filename, '.txt'),
    batch==2 ~ paste0('v2/txt/', filename, '.txt'),
))

# Drop opinion pieces
df.v0.3 <- df.v0.2 %>% filter(
    !(tolower(section) %in% c('opinion', 'lettetrs to the editor', 'opinions'))
)

# Mark climate policy articles
df.v0.3 %>% mutate(
    is_policy_article_kw = str_detect(tolower(excerpt), 
    'regulation|policy|policies|legislation|bill|green new deal|paris|environmental protection agency|clean power plan'
)) %>% write_tsv(here('code/articles/relevant.metadata.clean.tsv'))

