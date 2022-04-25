library(haven)
library(tidyverse)
filenames <- dir('nyt-metadata', full.names=TRUE)


read_nyt <- function(filename) {
    # read the nyt df and only select a few columns so that the resulting data isn't gargantuan
    df <- read.csv(filename, sep='\t') %>% 
        select(c('type_of_material', 'headline', 'web_url', 'pub_date', 'section_name')) %>% 
        filter(section_name %in% c('Opinion', "Climate", "Science", "U.S.", "World", "Education"))
        %>% sample_n(1000)
    df
}

dflist <- lapply(filenames, read_nyt)

df <- do.call(rbind,dflist) %>% sample_n(200)
write_tsv(df, 'nyt-sample-200.tsv')
