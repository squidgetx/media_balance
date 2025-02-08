source(here::here('code/setup.R'))

df.trim <- readRDS(here('code/journalists/authors.patched.rds'))

df.trim <- df.trim %>% mutate(
    elite_undergrad_25 = str_detect(
        tolower(edu.undergrad), 
        "brown|cornell|yale|harvard|columbia|princeton|dartmouth|mit|massachusetts institute of tech|upenn|stanford|university of pennsylvania|caltech|duke|johns hopkins|northwestern|university of chicago|berkeley|ucla|university of california, los angeles|rice|vanderbilt|notre dame|ann arbor|university of michigan|georgetown|chapel hill|carnegie mellon|emory|louis|uva|university of virginia"),
    # ivy plus stanford and mit
    elite_undergrad_ivyplus = str_detect(
        tolower(edu.undergrad), 
        "brown|cornell|yale|harvard|columbia|princeton|dartmouth|mit|massachusetts institute of tech|stanford|upenn|university of pennsylvania")
)

journo_keywords = c(
    "writer",
    "report",
    "news",
    "times",
    "post",
    "tribune",
    "usa today",
    "journal",
    "correspondent",
    "writ",
    "paper",
    'editor',
    'bureau chief',
    'critic',
    'columnist'
)
keyword_re <- paste(journo_keywords, collapse = "|")

df.trim <- df.trim %>% mutate(
    jokn = str_count(replace_na(tolower(summary), ''), keyword_re),
    jokn = jokn + str_count(replace_na(tolower(headline), ''), keyword_re),
    jokn = jokn + str_count(replace_na(tolower(occupation), ''), keyword_re),
    jokn = jokn + str_count(replace_na(tolower(exp.titles), ''), keyword_re),

    # Clean edu fields to remove unnecessary whitespace
    edu.undergrad = str_remove_all(edu.undergrad, "[\r\n]"),
    edu.field = str_remove_all(edu.field, "[\r\n]"),
)

saveRDS(df.trim, here('code/journalists/authors.edu.rds'))
