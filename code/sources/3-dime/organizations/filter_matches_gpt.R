source(here::here('code/setup.R'))

matches.gpt <- read_tsv(here(
    'code/sources/3-dime/organizations/matches.gpt.stg2.tsv'
)) %>% select(name, organization, explanation, relation)

matches.hf <- read_tsv(here(
    'code/sources/3-dime/organizations/matches.bert.stg1.tsv'
))

matches.ts <- read_tsv(here(
    'code/sources/3-dime/organizations/matches.ts.stg0.tsv'
))

matches.all <- matches.ts %>% left_join(matches.hf) %>% left_join(matches.gpt)

table(matches.all$ts.sim.class, matches.all$sim.class, useNA='ifany')
table(matches.all$sim.class, matches.all$relation, useNA='ifany')

matches.all <- matches.all %>% mutate(
    match = case_when(
        relation == 'match' ~ T,
        sim.class == 'Match' ~ T,
        ts.sim.class == 'Match' ~ T,
        TRUE ~ F
    ),
    match_source = case_when(
        !is.na(relation) ~ 'GPT-4o',
        !is.na(sim.class) ~ 'BERT',
        TRUE ~ 'textsim'
    )
)

matches.all$match %>% table
table(matches.all$match, matches.all$match_source)
matches.all$match %>% table

# Investigate some random matches just to double check
set.seed(100)
matches.all %>% filter(match)  %>% group_by(match_source) %>% sample_n(10) %>% select(name, organization, match_source) %>% kable()
# looks pretty good honestly
set.seed(101)
matches.all %>% filter(!match) %>% group_by(match_source) %>% sample_n(10) %>% select(name, organization, match_source) %>% kable()
# 100% success rate for negatives

matches.pos <- matches.all %>% filter(match) %>% 
    select(name, organization, cfscore, match_source, entity_id, cids) %>% arrange(entity_id)
matches.all$entity_id %>% unique() %>% length
# 20K organizations
matches.pos$entity_id %>% unique() %>% length
# Only 4K matched to DIME :(

matches.agg <- matches.pos %>% group_by(entity_id, organization) %>% summarize(
    cfscoresd = sd(cfscore),
    cfscore.median = median(cfscore),
    cfscore = mean(cfscore),
    dime.n = n(),
    cids = paste(cids, collapse=',')
) 

matches.agg$cfscoresd %>% hist
matches.agg %>% filter(cfscoresd > 1.5) %>% kable

matches.all %>% write_tsv(here('code/sources/3-dime/organizations/matches.all.tsv'))
matches.agg %>% write_tsv(here('code/sources/3-dime/organizations/matches.agg.tsv'))

