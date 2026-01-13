load("/scratch/project_2010938/Taavi_new/moisturedata/lithuania/KCG_2023.RData")
load("/scratch/project_2010938/Taavi_new/moisturedata/lithuania/KCG_2024.RData")

# select wanted columns from Lithuanian data
KCG_2023 <- KCG_2023 %>%
  select(Date, Label, "Obs#", ID, co2_flux, "IV T1", "IV H2O")

KCG_2024 <- KCG_2024 %>%
  select(Date, Label, "Obs#", ID, co2_flux, "IV T1", "IV H2O")

# Combine into one dataframe
KCG <- rbind(KCG_2023, KCG_2024)

# rename to match db
names(KCG) <- c("date", "subsiteid", "point", "pointtype", "j_flux", "t05", "tsmoisture")

# add siteid
KCG$siteid <- "Kacergine"

# read in the database file
db <- read.csv("/scratch/project_2010938/Taavi_new/hs-combined-2025-09-29.csv", header = TRUE)

# change KGC$date to character
KCG <- KCG %>%
  mutate(
    date = as.character(date),
    point = as.character(point)
  )

# combine datasets
db_lt_added <- dplyr::bind_rows(db, KCG)

# save to new file (date 11.11.2025)
write.csv(db_lt_added, file = "/scratch/project_2010938/Taavi_new/hs-combined-2025-11-11.csv", row.names = FALSE)
