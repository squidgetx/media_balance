#!/usr/bin/env Rscript

# This script takes an input of articles tsv with columns name, link, and error generated
# from journalist_extractor.py
# and outputs a unique tsv of journalist information and a separate tsv of errors
library(tidyverse)

args <- commandArgs(trailingOnly = TRUE)

df <- read_tsv(args[1])
df %>%
    filter(!is.na(link)) %>%
    select(name, link, hostname) %>%
    unique() %>%
    write_tsv(args[2])
df %>%
    filter(is.na(link)) %>%
    filter(is.na(error)) %>%
    unique() %>%
    write_tsv(paste0(tools::file_path_sans_ext(args[1]), ".partial.tsv"))

df %>%
    filter(!is.na(error)) %>%
    write_tsv(paste0(tools::file_path_sans_ext(args[1]), ".errors.tsv"))
