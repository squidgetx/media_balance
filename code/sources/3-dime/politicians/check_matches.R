source(here::here('code/setup.R'))

load(here("code/sources/3-dime/data/dime_recipients_1979_2022.rdata"))
# cands for cfscores

cand.pairs.raw <- read_tsv(
    here("code/sources/3-dime/politicians/match-candidates.tsv"),
    show_col_types = F
)
pols <- read_tsv(
    here("code/sources/3-dime/politicians/politicians.states.tsv"),
    show_col_types = F
)

dime.pols <- read_tsv(
    here("code/sources/3-dime/politicians/dime-politicians.tsv"),
    show_col_types = F
) %>%
    group_by(Cand.ID) %>%
    summarize(
        dime_states = unique(paste(state, collapse = ",")),
        person_name = first(person_name)
    )

stopifnot(length(unique(dime.pols$Cand.ID)) == nrow(dime.pols))
stopifnot(length(unique(pols$person_name)) == nrow(pols))


cand.pairs <- cand.pairs.raw %>%
    left_join(pols %>% select(person_name, state)) %>%
    left_join(dime.pols %>% select(Cand.ID, dime_states)) %>%
    mutate(
        jw_sim = stringdist::stringsim(person_name, dime_name, method = "jw", p = 0.1),
        cosine_sim = stringdist::stringsim(person_name, dime_name, method = "cosine"),
        jaccard = stringdist::stringsim(person_name, dime_name, method = "jaccard"),
        cb = jw_sim + cosine_sim + jaccard,
        state_match = state %in% dime_states,
    )
if (F) {
    # Choose thresholds for matching with qualitative judgement
    cand.pairs %>%
        filter(
            !state_match, cb < 3
        ) %>%
        arrange(desc(cb)) %>%
        select(dime_name, person_name, cb, dime_states, state) %>%
        head(20)

    cand.pairs %>%
        filter(
            state_match, cb > 2.5
        ) %>%
        arrange(cb) %>%
        select(dime_name, person_name, cb, dime_states, state) %>%
        head(100) %>%
        kable()

    cand.pairs %>%
        filter(
            state_match, cb > 2.8
        ) %>%
        arrange(cb) %>%
        select(dime_name, person_name, cb, dime_states, state) %>%
        head(20)
}

cand.pairs <- cand.pairs %>%
    mutate(
        match = case_when(
            state_match & cb > 2.5 ~ TRUE,
            !state_match & cb > 2.97 ~ TRUE,
            !state_match & cb > 2.96 & dime_name %in% c("bill deblasio", "annette tadeo") ~ TRUE,
            TRUE ~ FALSE
        )
    ) %>%
    mutate(
        # Manual corrections for low cbs
        match = case_when(
            dime_name == "ken fuller" & person_name == "jean fuller" ~ F,
            dime_name == "chris bos" & person_name == "cheri bustos" ~ F,
            dime_name == "mitchell ing" & person_name == "mitchell englander" ~ F,
            dime_name == "carlos pena" & person_name == "carlos menchaca" ~ F,
            dime_name == "jeff c wheeland" & person_name == "jeff leach" ~ F,
            dime_name == "rick karl" & person_name == "ricky arriola" ~ F,
            dime_name == "vincent a ene" & person_name == "vincent sapienza" ~ F,
            TRUE ~ match
        )
    )

# 394 true matches... OK I guess
# For now we use non period-specific DIME scores to simplify the analysis
cfscores <- cands %>%
    filter(recipient.type == "cand") %>%
    group_by(Cand.ID) %>%
    summarize(
        cfscore = mean(recipient.cfscore, na.rm = T),
        cfscore_n = n()
    )
cfscores.linked <- cand.pairs %>%
    filter(match) %>%
    left_join(
        cfscores,
        by = c("Cand.ID")
    ) %>%
    select(cfscore, cfscore_n, person_name, Cand.ID, dime_name) %>%
    group_by(person_name) %>%
    mutate(
        cfscore_mean = mean(cfscore, weights = cfscore_n)
    )
# Print some example matches
cfscores.linked %>%
    select(person_name, dime_name, cfscore) %>%
    distinct() %>%
    head(10) %>%
    kable()

cfscores.agg <- pols %>%
    left_join(
        cfscores.linked %>%
            select(person_name, cfscore_mean) %>%
            distinct()
    ) %>%
    select(person_name, cfscore_mean)
cfscores.agg %>% filter(
    str_detect(person_name, "gavin newsom|mitch mcconnel|barack obama|ron paul")
)
cfscores.agg %>% write_tsv(here("code/sources/3-dime/politicians/politician.cfscores.tsv"))

sources <- read_tsv(here("code/sources/3-dime/organizations/sources.dime.orgs.tsv"), show_col_types = F)
sources.dime <- sources %>%
    mutate(pnl = tolower(person_name)) %>%
    left_join(
        cfscores.agg %>% rename(pnl = "person_name") %>% mutate(
            category = "government"
        )
    ) %>%
    mutate(
        cfscore_src = case_when(
            !is.na(cfscore_mean) ~ "politician",
            !is.na(cfscore) ~ "organization",
            TRUE ~ NA,
        ),
        cfscore = case_when(
            !is.na(cfscore_mean) ~ cfscore_mean,
            TRUE ~ cfscore
        )
    ) %>%
    select(!c(pnl, cfscore_mean))

table(sources.dime$cfscore %>% is.na(), sources.dime$cfscore_src, useNA='ifany')
table(sources.dime$cfscore %>% is.na(), sources.dime$cfscore_src, useNA='ifany') %>% prop.table()

sources.dime %>% write_tsv(
    here("code/sources/3-dime/politicians/sources.dime.orgs.pols.tsv")
)
