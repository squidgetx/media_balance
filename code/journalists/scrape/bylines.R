library(tidyverse)
library(tidyjson)

df.nyt <- read_json('data/nyt-authors.jsonl') %>% spread_all() %>% 
    select(href, name) %>% mutate(
        title=NA,
        source='New York Times',
    )
df.wapo <- read_json('data/wapo-authors.jsonl') %>% spread_all() %>%
    mutate(
        title=NA,
        source='The Washington Post',
        name=str_split(text, " - ", simplify=T)[,1]
    ) %>% select(href, title, name, source)

df.lat <- read_json('data/lat-authors.jsonl') %>% spread_all() %>%
    select(href, name) %>% mutate(
        title=NA,
        source='Los Angeles Times',
    )

df.ct <- read_json('data/ct-authors.jsonl') %>% spread_all() %>%
    mutate(
        title=NA,
        source='Chicago Tribune',
        name=text
    ) %>% select(href, title, name, source)

# Function to select the first non-NA element
# I hate R
select_first_non_na <- function(x) {
  first_non_na <- na.omit(x)[1]
  if (is.na(first_non_na)) NA else first_non_na
}

df.usat <- read_json('data/usatoday-authors.jsonl') %>% spread_all() %>%
    enter_object("links") %>%
    gather_array() %>%
    spread_values(url = jstring()) %>% 
    mutate(
        twitter = ifelse(str_detect(url, "twitter"), url, NA),
        href = ifelse(str_detect(url, "usatoday.com/staff"), url, NA),
        email = ifelse(str_detect(url, "mailto"), url, NA),
    ) %>% group_by(name, title) %>%
    summarize(
        twitter=select_first_non_na(twitter), 
        href=select_first_non_na(href), 
        email=select_first_non_na(email)
    ) %>%
    mutate(source='USA Today') %>% select(
        name, title, source, twitter, href, email
    )

extract_string <- function(input_string) {
  parts <- str_split(input_string, " — | at ", simplify = T)
  if (length(parts) >= 2) {
    result <- str_trim(parts[,2])
  } else {
    result <- NA
  }
  return(result)
}

df.wsj <- read_json('data/wsj-authors.jsonl') %>% spread_all() %>%
    mutate(
        name=str_split(text, " — | at", simplify=T)[,1],
        title=unlist(lapply(text, extract_string), use.names=F),
        source='Wall Street Journal',
    ) %>% select(href, title, name, source)



df <- rbind(df.nyt, df.wapo, df.lat, df.ct, df.wsj) %>% mutate(
    twitter=NA,
    email=NA
)  %>% as.tibble() %>% rbind(df.usat)

write_tsv(df, 'data/bylines.tsv')

