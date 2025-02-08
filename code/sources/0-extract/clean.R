# R code to clean sources - first stage
# First stage cleaning involves basic row-wise cleaning including fixing category names
# and assigning organization and person IDs
# The next step after the first stage cleaning is to deduplicate organizations
# Once organizations are deduplicated, we can start stage 2 

source(here::here('code/setup.R'))

sources <- read_tsv(here('code/sources/0-extract/sources.raw.tsv')) %>% mutate(
    category = tolower(category), 
    person_title = tolower(person_title),
    organization = tolower(organization),
    document = tolower(document),
    src_id = row_number()
) 
sources[sources=='N/A'] <- NA
sources[sources=='n/a'] <- NA

# Clean the source categories into basic categories
sources <- sources %>% mutate(
    is_gov = str_detect(category, 'government|bureaucrat|politician|state|political|international|legis'),
    is_legal = str_detect(category, 'legal|law|attorn|jud|court'),
    is_advocacy = str_detect(category, 'advocacy|nonprofit|lobbyist|interest|activist|union|think tank'),
    is_business = str_detect(category, 'industry|business|corporation|financ'),
    is_academic = str_detect(category, 'academic|research|académico'),
    is_media = str_detect(category, 'media|author|writer'),
    is_citizen = str_detect(category, 'citizen|relig|art|sport|athlete|film|music'),
) %>% mutate(
    category.clean = case_when(
        str_detect(category, 'international') ~ 'international',
        is_gov ~ 'government',
        is_advocacy ~ 'advocacy',
        is_business ~ 'business',
        is_media ~ 'media',
        is_academic ~ 'academic',
        is_citizen ~ 'citizen',
        TRUE ~ 'other'
    ), 
) %>% select(!starts_with('is_'))
table(sources$category.clean, useNA='ifany')


# Deduplicate people
# Same category and same name is good enough to make a match
ppl.names <- sources %>% filter(!is.na(person_name)) %>% 
    select(person_name, category) %>% 
    distinct() %>% mutate(
        person_id = row_number()
    )

sources %>% left_join(ppl.names) %>% write_tsv(here('code/sources/0-extract/sources.clean.tsv'))

# Deduplicate organizations 
# This is harder. First, use simple exact matching.
#org.names <- sources %>% filter(!is.na(organization)) %>% 
#    select(organization, category.clean) %>% mutate(
#        org_id = row_number()
#    )
#org.names %>% write_tsv(here('code/sources/dedup/orgs.raw.tsv'))
#sources %>% left_join(org.names) %>% group_by(org_id) %>% summarize(n=n()) %>% 
#    left_join(org.names) %>% write_tsv(here('code/sources/dedup/orgs.raw.tsv'))

