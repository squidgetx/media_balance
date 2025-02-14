source(here::here("code/setup.R"))
pacman::p_load(rlang)

# Load the data

datadir <- "data/masterdata"
all.articles <- read_tsv(here(datadir, "articles.tsv"))
all.sources <- read_tsv(here(datadir, "sources.tsv"))
sources <- all.sources %>% filter(policy_label_gpt)
articles <- all.articles %>% filter(policy_label_gpt)
authors <- articles %>%
    group_by(author_name, elite_undergrad_ivyplus, edu.undergrad, edu.has_postgrad, is_career, field.journo, age_est_2017, gender, race.nonwhite) %>%
    summarize(n = n()) %>%
    filter(!is.na(author_name))
articles.repna <- articles %>% mutate(
    field.journo = replace_na(field.journo, FALSE),
    elite_undergrad_ivyplus = replace_na(elite_undergrad_ivyplus, FALSE),
    edu.has_postgrad = replace_na(edu.has_postgrad, FALSE),
)
sources.repna <- sources %>% mutate(
    field.journo = replace_na(field.journo, FALSE),
    elite_undergrad_ivyplus = replace_na(elite_undergrad_ivyplus, FALSE),
)

make_cfscore <- function(
    df,
    cfscore.options = list(pols = F, impute.all = F, impute.off = F, nwd.sd.thresh = 0.8)) {
    df %>% mutate(
        # Raw org cfscore is the raw match value if
        # 1. the category is in a list of approved categories
        # 2. the cfscore_sd is less than the provided threshold
        # Lower threshold means the matches are higher quality
        org.with.cfscore = category %in% c("Advocacy", "Business", "Other", "Citizen"),
        cfscore.org.raw = case_when(
            !org.with.cfscore ~ NA,
            is.na(cfscoresd) ~ cfscore.raw,
            !check_(cfscore.options$nwd.sd.thresh) ~ cfscore.raw,
            cfscoresd > check_(cfscore.options$nwd.sd.thresh) ~ NA,
            TRUE ~ cfscore.raw
        ),
        # Next, we impute any missing data.
        # If the "impute off" option is specified we don't do any imputation
        # If the "impute all" option is specified we replace raw data with imputed data
        # Otherwise, we use the raw match when we have it and the imputed one when we don't
        cfscore.org = case_when(
            !org.with.cfscore ~ NA,
            check_(cfscore.options$impute.off) ~ cfscore.org.raw,
            check_(cfscore.options$impute.all) ~ cfscore.i2,
            !is.na(cfscore.org.raw) ~ cfscore.org.raw,
            TRUE ~ cfscore.i2
        ),
        # Finally, we construct the usable cfscore data.
        # Mostly it's just the cfscore.org data.
        # But the use.pols also adds in politician data
        # This should not really be used IMO because it's easier to do it
        # separately
        cfscore.use = case_when(
            !check_(cfscore.options$pols) ~ cfscore.org,
            cfscore_src == "politician" ~ cfscore.raw,
            TRUE ~ cfscore.org
        ),
    )
}

# Helper function to calculate balance based on many different possible
# specifications.
calculate_balance <- function(
    df,
    types = c("party", "org_category", "cfscore", "topic"),
    cfscore.options = list(pols = F, impute.all = F, impute.off = F, nwd.sd.thresh = NA),
    ff_only = T,
    thresh = 0.2,
    articles_df = articles.repna) {
    rtypes <- c()
    ltypes <- c()
    if ("party" %in% types) {
        ltypes <- c(ltypes, "dem")
        rtypes <- c(rtypes, "rep")
    }
    if ("org_category" %in% types) {
        ltypes <- c(ltypes, "env")
        rtypes <- c(rtypes, ifelse(ff_only, "ff", "bus"))
    }
    if ("cfscore" %in% types) {
        ltypes <- c(ltypes, "left")
        rtypes <- c(rtypes, "right")
    }
    if ("topic" %in% types) {
        ltypes <- c(ltypes, "topic_environ")
        rtypes <- c(rtypes, "topic_business")
    }
    left_expr <- paste0(ltypes, collapse = "|") %>% parse_expr()
    right_expr <- paste0(rtypes, collapse = "|") %>% parse_expr()
    df %>%
        make_cfscore(cfscore.options) %>%
        mutate(
            left = cfscore.use < 0 - thresh,
            right = cfscore.use > thresh,
            env = category.slant == "Environmental",
            ff = category.slant == "Fossil Fuel",
            bus = category == "Business",
            dem = pol_party == "Democrat",
            rep = pol_party == "Republican",
            topic_business = src_topic == "Business",
            topic_environ = src_topic == "Environment",
        ) %>%
        group_by(textfile, date, source) %>%
        summarize(
            n_left = sum(!!left_expr, na.rm = T),
            n_right = sum(!!right_expr, na.rm = T),
            cfscore = mean(cfscore.use, na.rm = T),
            cfscore.median = median(cfscore.use, na.rm = T),
            cfscore.sd = sd(cfscore.use, na.rm = T),
            n = n()
        ) %>%
        mutate(
            balance = ifelse(
                n_left + n_right > 0,
                n_left > 0 & n_right > 0,
                NA
            ),
            diff_normalized = (n_right - n_left) / n
        ) %>%
        left_join(articles_df)
}

j_covars <- function(age = 37) {
    c(
        "elite_undergrad_ivyplus",
        "edu.has_postgrad",
        "field.journo",
        sprintf("(age_est_2017 > %s)", age),
        "gender",
        "race.nonwhite"
    )
}

make_fmla <- function(y, covariates = j_covars(), festring = "| year + source") {
    covariate_str <- paste0(covariates, collapse = "+")
    as.formula(paste(y, "~", covariate_str, festring))
}

make_models <- function(df, yvars, covariates = j_covars(), festring = "| year + source", cluster = "author_name") {
    lapply(yvars, \(y) {
        feols(make_fmla(y, covariates, festring), data = df, cluster = cluster)
    })
}


theme_min <- theme_bw() + theme(
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank()
)
