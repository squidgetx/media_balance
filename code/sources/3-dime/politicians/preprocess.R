# Script to add politician DIME ideology cfscores to the sources dataset
source(here::here('code/setup.R'))

load(here("code/sources/3-dime/data/dime_recipients_1979_2022.rdata"))
# loads into variable `cands`

# probably should reorganize that at some point lol
pols <- read_tsv(here("code/sources/2-supplement/politicians.tsv")) %>%
    mutate(
        fname = str_split_i(person_name, " ", 1),
        lname = str_split_i(person_name, " ", -1),
        person_name = tolower(person_name)
    ) %>%
    filter(!is.na(person_name)) %>%
    group_by(person_name) %>%
    summarize(titles = first(titles), organizations = first(organizations))

cand.names <- cands %>%
    filter(recipient.type == "cand") %>%
    mutate(
        person_name = paste(ffname, lname, suffix)
    ) %>%
    select(person_name, fname, lname, Cand.ID, state) %>%
    unique()

cand.names %>% write_tsv(
    here("code/sources/3-dime/politicians/dime-politicians.tsv")
)
pols %>% write_tsv(
    here("code/sources/3-dime/politicians/politicians.tsv")
)
