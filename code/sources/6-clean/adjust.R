# Final ish cleaning before we join with the rest of the data
source(here::here("code/setup.R"))

df <- read_tsv(here("code/sources/6-clean/sources.clean.tsv")) %>% mutate(
    # Clean up category names
    category = case_when(
        gov_category == "US politician" ~ "Politician",
        gov_category == "US bureaucrat" ~ "Bureaucrat",
        category == "government" ~ "International",
        category == "citizen" ~ "Other",
        TRUE ~ stri_trans_totitle(category)
    ),
    category.slant = case_when(
        category.slant == "Non-US" ~ "International",
        category.slant == "citizen" ~ "Other",
        !is.na(pol_party) ~ pol_party,
        category.slant == "government" ~ "Bureaucrat",
        category.slant == "US Politician" ~ "Bureaucrat", # These are the ones we did not identify party for
        TRUE ~ stri_trans_totitle(str_remove_all(category.slant, "US"))
    ),

    # Clean up cfscores
    cfscore.raw = cfscore,
    # DIME cfscores are most valid for politicians, advocacy, business, and 'other' organizations
    # Note that we also have cfscores for media, academic sources, and gov't organizations
    # These are usually nonsensical.
    cfscore.well_defined = case_when(
        cfscore_src == "politician" ~ TRUE,
        category %in% c("Advocacy", "Business", "Other", "Citizen") ~ TRUE,
        TRUE ~ FALSE
    ),
    cfscore = ifelse(cfscore.well_defined, cfscore.raw, NA),

    # The imputed cfscore is also restricted to well defined only
    cfscore.impute = case_when(
        !is.na(cfscore) ~ cfscore,
        cfscore.well_defined ~ cfscore.i2,
        TRUE ~ NA
    ),

    # Impute political parties using cfscore where missing
    # Only for politicians though.
    pol_party = case_when(
        !is.na(pol_party) ~ pol_party,
        cfscore_src != "politician" ~ NA,
        cfscore.raw < 0 ~ "Democrat",
        cfscore.raw > 0 ~ "Republican",
        TRUE ~ NA
    ),
)


# Manually fix "White House" entries
# Should be "politician" and we should merge with the "obama/biden/trump" administration entries
articles <- read_tsv(here("data/articles/articles.clean.tsv")) %>% select(textfile, date)
df.articles <- df %>%
    rename(textfile = filename) %>%
    left_join(articles)

get_admin_id <- function(admin) {
    df.articles %>%
        filter(str_detect(organization_name, paste(admin, "Administration"))) %>%
        .$org_id %>%
        fmode()
}
admin_ids <- sapply(c("Obama", "Trump", "Biden"), get_admin_id)

org_info <- df %>%
    filter(org_id %in% admin_ids) %>%
    select(org_id, organization_name, organization_description) %>%
    distinct()
stopifnot(nrow(org_info) == 3)
wh <- df.articles %>%
    filter(organization_name == "The White House") %>%
    mutate(
        org_id = case_when(
            year(date) <= 2016 ~ admin_ids["Obama"],
            year(date) <= 2020 ~ admin_ids["Trump"],
            TRUE ~ admin_ids["Biden"]
        )
    ) %>%
    rows_update(org_info, by = "org_id")
# Also update the pol party of each of the admins
df.wh <- df.articles %>%
    rows_update(wh, by = "src_id") %>%
    mutate(
        pol_party =
            case_when(
                org_id == admin_ids['Obama'] ~ 'Democrat',
                org_id == admin_ids['Biden'] ~ 'Democrat',
                org_id == admin_ids['Trump'] ~ 'Republican',
                TRUE ~ pol_party
            )
    ) 

df.wh %>% write_tsv(here("code/sources/6-clean/sources.adjust.tsv"))
