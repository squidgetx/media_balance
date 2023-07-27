# Load required library (install if not already installed)
if (!requireNamespace("data.table", quietly = TRUE)) {
    install.packages("data.table")
}
library(data.table)

# Check if the command line argument is provided
if (length(commandArgs(trailingOnly = TRUE)) == 0) {
    cat("Usage: Rscript script.R input_file.tsv\n")
    quit(save = "no")
}

# Read the input TSV file from command line argument
input_file <- commandArgs(trailingOnly = TRUE)[1]
data <- fread(input_file, sep = "\t", header = TRUE)

# Filter out rows where label is "false"
filtered_data <- data[label == TRUE]

# Write the filtered TSV to standard output
write.table(filtered_data, sep = "\t", row.names = FALSE, quote = FALSE)
