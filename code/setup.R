# Simple setup code common to most R scripts in the project

# Essential libraries
# Load with pacman

# general workflow libraries
pacman::p_load(here)
pacman::p_load(tidyverse)
pacman::p_load(knitr)
pacman::p_load(tictoc)

# utility stats/types
pacman::p_load(lubridate)
pacman::p_load(stats)
pacman::p_load(scales)
pacman::p_load(zoo)
pacman::p_load(collapse)

# string manipulation
pacman::p_load(stringr)
pacman::p_load(stringi)
pacman::p_load(stringdist)
pacman::p_load(fedmatch)

# text as data
pacman::p_load(quanteda)
pacman::p_load(quanteda.textmodels)
pacman::p_load(quanteda.textstats)

# machine learning
pacman::p_load(caret)
pacman::p_load(pROC)

# regression analysis
pacman::p_load(fixest)
pacman::p_load(glmnet)
pacman::p_load(expss)
pacman::p_load(stargazer)
pacman::p_load(broom)

# ggplot extensions
pacman::p_load(ggfixest)
pacman::p_load(ggrepel)
pacman::p_load(ggpubr)

knitr::opts_chunk$set(warning = FALSE, message = FALSE)


read_tsv <- function(...) {
    readr::read_tsv(..., show_col_types=F)
}

read_csv <- function(...) {
    readr::read_csv(..., show_col_types=F)
}

#source(here::here('code/setup.R'))
