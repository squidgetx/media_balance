source(here::here("code/setup.R"))
datadir <- "data/masterdata2"

sources <- read_tsv(here("code/sources/sources.tsv"))

articles <- read_tsv(here("data/articles/articles.clean.tsv"))

authors <- readRDS(here("code/journalists/authors.clean.rds"))  %>% filter(!is.na(author_name))

articles.authors <- articles %>%
    mutate(
        clean_name = tolower(author) %>%
            str_remove("^and ") %>%
            str_remove("^-") %>%
            str_split_i(";", 1) %>%
            str_split_i("/", 1)
    ) %>%
    left_join(authors, by = c("clean_name")) %>% 
    mutate(
        ## Article level data
        post2017 = date > as.Date("2017/01/01"),
        year.q = quarter(date, with_year = T),
        year = year(date),
        newspaper_lean = case_when(
            str_detect(source, "Wall St") ~ "RIGHT",
            str_detect(source, "New York") ~ "LEFT",
            str_detect(source, "Washington") ~ "LEFT",
            str_detect(source, "Los Angeles") ~ "LEFT",
            str_detect(source, "Chicago Tribune") ~ NA,
            str_detect(source, "USA Today") ~ NA,
        ),

        ## Journalist level data - varies by article because it uses year
        is_career = exp.year_start_journo == exp.year_start,
        years_nonj = exp.year_start_journo - exp.year_start,
        field.journo = str_detect(tolower(edu.field), "journal|comm|media"),
        field.political = str_detect(tolower(edu.field), "political|gov"),
        race.nonwhite = pred.race != "white",
       
        age_est_2017 = case_when(
            !is.na(edu.grad_year) ~ 2017 - edu.grad_year + 22,
            !is.na(exp.year_start) ~ 2017 - exp.year_start + 22,
            TRUE ~ NA
        ),
        age_est = year - 2017 + age_est_2017,
        age_gt30 = age_est >= 30,
    ) %>%
    mutate_if(is_character, \(x) str_remove_all(x, "[\r\n\t]"))

aggregate_outcomes <- function(df) {
    df %>%
        mutate(
            cfscore_pol = ifelse(cfscore_src == "politician", cfscore, NA),
            cfscore_org = ifelse(cfscore_src == "politician", NA, cfscore),
        ) %>%
        summarize(
            n = n(),
            n_env = sum(category.slant == "Environmental", na.rm = T),
            n_ff = sum(category.slant == "Fossil Fuel", na.rm = T),
            n_bus = sum(category.slant == "Business", na.rm = T) + n_ff,
            n_dem = sum(pol_party == "Democrat", na.rm = T),
            n_rep = sum(pol_party == "Republican", na.rm = T),
            n_left_dime = sum(cfscore < -0.2, na.rm = T),
            n_right_dime = sum(cfscore > 0.2, na.rm = T),
            n_left_dime_other = sum(cfscore < -0.2 & !c(category.slant %in% c("Environmental", "Fossil Fuel", "Democrat", "Republican")), na.rm = T),
            n_right_dime_other = sum(cfscore > 0.2 & !c(category.slant %in% c("Environmental", "Fossil Fuel", "Democrat", "Republican")), na.rm = T),
            n_unique_source_category = length(unique(category)),
            prop_env = n_env / n,
            prop_bus = n_bus / n,
            prop_ff = n_ff / n,
            prop_dem = n_dem / n,
            prop_rep = n_rep / n,
            prop_left_dime = n_left_dime / n,
            prop_right_dime = n_right_dime / n,
            diff_ff_env = n_ff - n_env,
            diff_bus_env = n_bus - n_env,
            diff_rep_dem = n_rep - n_dem,
            balance_bus_env = case_when(
                n_env + n_bus > 0 ~ n_env >= 1 & n_bus >= 1,
                TRUE ~ NA
            ),
            balance_ff_env = case_when(
                n_env + n_ff > 0 ~ n_env >= 1 & n_ff >= 1,
                TRUE ~ NA
            ),
            balance_rep_dem = case_when(
                n_rep + n_dem > 0 ~ n_dem >= 1 & n_rep >= 1,
                TRUE ~ NA
            ),
            # Various balance measures
            n_left_total = n_env + n_left_dime_other + n_dem,
            n_right_total = n_ff + n_right_dime_other + n_rep,
            n_center_total = n - n_left_total - n_right_total,
            bal.at_least_one_both_sides = case_when(
                n_left_total + n_right_total > 0 ~ n_left_total >= 1 & n_right_total >= 1,
                TRUE ~ NA
            ),
            bal.strictly_neutral = n_center_total == n,
            bal.diff_lr_normalized = abs(n_left_total - n_right_total) / n,
            bal.diff_lr_normalized_nonabs = (n_left_total - n_right_total) / n,
            balance_all = case_when(
                n_env + n_ff + n_right_dime + n_left_dime + n_rep + n_dem > 0 ~
                    n_ff + n_right_dime + n_rep >= 1 & n_env + n_left_dime + n_dem >= 1,
                TRUE ~ NA
            ),
            ideo.mean = mean(cfscore, na.rm = T),
            ideo.mean.i = mean(cfscore.impute, na.rm = T),
            ideo.mean.i.orgs = mean(cfscore_org, na.rm = T),
            ideo.mean.pols = mean(cfscore_pol, na.rm = T),
            ideo.sd.i = sd(cfscore.impute, na.rm = T),
            ideo.sd.orgs = sd(cfscore_org, na.rm = T),
            ideo.sd.pols = sd(cfscore_pol, na.rm = T),
            n_topic_business = sum(src_topic == "Business", na.rm = T),
            n_topic_environment = sum(src_topic == "Environment", na.rm = T),
            n_topic_policy = sum(src_topic == "Policy", na.rm = T),
            diff_topic_bus_env = n_topic_business - n_topic_environment,
            prop_topic_business = n_topic_business / n,
            prop_topic_environment = n_topic_environment / n,
            prop_topic_policy = n_topic_policy / n,
        )
}

sources.articles.authors <- sources %>% left_join(articles.authors) %>%
    filter(!is.na(filename))

articles.clean <- sources.articles.authors %>%
    group_by(filename) %>%
    aggregate_outcomes() %>%
    left_join(articles.authors)

## Predicted ideology - todo, do this somewhere else
full.model <- lm(ideo.mean.i ~ field.political + field.journo + elite_undergrad_ivyplus + gender + pred.race + is_career, data = articles.clean)
scores <- predict(full.model, newdata = articles.clean %>% mutate(pred.race = ifelse(pred.race == "other", NA, pred.race)))
articles.clean$pred.ideo <- scores
articles.clean$pred.ideo.cut <- scores > mean(scores, na.rm = T)
articles.clean$pred.ideo.q <- cut(
    scores,
    quantile(scores, na.rm = T),
    labels = c("0-25 (Most Liberal)", "25-50", "50-75", "75-100 (Most Conservative)")
)

author_columns <- c("author_name", intersect(colnames(authors), colnames(articles.authors)))
authors.clean <- sources.articles.authors %>%
    group_by(author_name) %>%
    aggregate_outcomes() %>%
    left_join(articles.authors %>% select(all_of(author_columns))) %>%
    distinct(author_name, .keep_all = T)

sources.articles.authors %>%
    write_tsv(here(datadir, "sources.tsv"))
articles.clean %>% write_tsv(here(datadir, "articles.tsv"))
authors.clean %>% write_tsv(here(datadir, "authors.tsv"))

# Write orgs separately as well for auditing purposes
orgs <- sources %>%
    group_by(org_id, organization_name, organization_description, cfscore, cfscore.i2) %>%
    summarize(
        n = n(),
    )
orgs %>% write_tsv(here(datadir, "organizations.tsv"))
