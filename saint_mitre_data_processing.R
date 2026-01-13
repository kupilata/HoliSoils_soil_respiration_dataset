library(dplyr)
library(readr)

# set wd
setwd("/scratch/project_2010938/Taavi_new")

# Folder containing your TXT files
folder_path <- "moisturedata/saint_mitre"

# List all .TXT files (case-insensitive)
files <- list.files(folder_path, pattern = "\\.txt$", full.names = TRUE, ignore.case = TRUE)

# Initialize list to store all results
sm_covariates <- list()

# Initialize vector to store files with unmatched STARTs
mismatched_files <- character(0)

# Columns to compute mean for
mean_cols <- c("Tsoil", "Tair", "Msoil")

for (f in files) {
  # Read all lines
  lines <- read_lines(f)
  
  # Remove 'zero' lines and blank lines
  lines <- lines[!grepl("^zero$", lines, ignore.case = TRUE)]
  lines <- lines[lines != ""]
  
  # Identify START and END positions
  start_idx <- grep("^\\s*START\\s*$", lines, ignore.case = TRUE)
  end_idx   <- grep("^\\s*END\\s*$", lines, ignore.case = TRUE)
  
  # Handle extra ENDs: only keep ENDs that come after a START
  valid_ends <- end_idx[sapply(end_idx, function(e) any(start_idx < e))]
  
  # Pair each START with the next valid END
  paired_blocks <- lapply(start_idx, function(s) {
    e <- valid_ends[valid_ends > s][1]  # first END after this START
    if (is.na(e)) return(NULL)          # unmatched START
    return(c(s, e))
  })
  paired_blocks <- paired_blocks[!sapply(paired_blocks, is.null)]
  
  # If there are unmatched STARTs, save file name for later
  if (length(paired_blocks) < length(start_idx)) {
    mismatched_files <- c(mismatched_files, f)
  }
  
  # Get header line
  colnames_line <- lines[1]
  all_names <- strsplit(colnames_line, ",")[[1]]
  
  # Store results for this file
  measurements <- list()
  
  for (block in paired_blocks) {
    s <- block[1]
    e <- block[2]
    
    # Extract block lines
    block_lines <- lines[(s + 1):(e - 1)]
    if (length(block_lines) == 0) next
    
    # Read block without header
    block_df <- read.csv(
      text = paste(block_lines, collapse = "\n"),
      header = FALSE,
      stringsAsFactors = FALSE,
      fill = TRUE,
      strip.white = TRUE
    )
    
    # Assign names from header for first N columns
    n_header <- length(all_names)
    colnames(block_df)[1:n_header] <- all_names
    
    # Compute mean for numeric columns that exist
    numeric_cols <- intersect(mean_cols, names(block_df))
    numeric_means <- block_df %>%
      summarise(across(all_of(numeric_cols), ~ mean(as.numeric(.x), na.rm = TRUE)))
    
    # Take first value for other columns
    nonnum_cols <- setdiff(names(block_df), numeric_cols)
    first_values <- block_df[1, nonnum_cols, drop = FALSE]
    
    # Combine results
    result_row <- bind_cols(first_values, numeric_means)
    measurements[[length(measurements) + 1]] <- result_row
  }
  
  if (length(measurements) > 0) {
    file_results <- bind_rows(measurements, .id = "measurement_id") %>%
      mutate(file = basename(f))
    sm_covariates[[f]] <- file_results
  }
}

# Combine all files into one tidy data frame
sm_covariates <- bind_rows(sm_covariates)

# View combined results
print(sm_covariates)

# Files with unmatched STARTs for manual inspection
print(mismatched_files)

write.csv(sm_covariates, paste0(folder_path, "/saint_mitre_combined.csv"), row.names = FALSE)
