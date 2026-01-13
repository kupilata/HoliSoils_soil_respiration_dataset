library(dplyr)
library(lubridate)
library(tidyr)
library(stringr)
library(ggplot2)
library(readr)

# Moisture joining
setwd("/scratch/project_2010938/Taavi_new/")

# Read in database file
db <- read.csv("holisoils_recoded.csv", header = TRUE, check.names = FALSE) # database file

print("Moisture distribution table before adding covariates")
db %>%
  group_by(siteid) %>%
  summarise(
    min = min(tsmoisture, na.rm = TRUE),
    max = max(tsmoisture, na.rm = TRUE),
    mean = mean(tsmoisture, na.rm = TRUE),
    n = n()
  ) %>%
  arrange(desc(max))

# update date and add row_id for preserving order
db <- db %>%
  mutate(
    date = as.Date(date),
    row_id = row_number() # preserve row order
  )

# ========
# KARSTULA
# ========

# Lets choose the columns of interests and calculate mean for each scout per day.
# define measuring points
measuring_points <- c("1C", "4N", "7C", "8N")
# define the base path
base_file <- "moisturedata/karstula/2025-02-01_soil-scout_export_"
# Choose columns that we are interested in
column_of_interest <- c("Timestamp..UTC.", "Scout.name", "Moisture")
# Create list for storage of data
karstula <- list()
for (i in measuring_points) {
  # name for reading the data
  name <- paste0("karstula_", i)
  
  # read the data and filter out unwanted columns
  df <- read.csv(paste0(base_file, name, ".csv"), header = TRUE)
  df <- df[, column_of_interest]
  
  # convert time
  df$Timestamp <- ymd_hms(df$Timestamp..UTC., tz = "UTC", quiet = TRUE)
  df$date <- as.Date(df$Timestamp)
  
  # calculate mean for each day / scout.name combination
  df <- df %>%
    group_by(date, Scout.name) %>%
    summarise(mean_value = mean(Moisture * 100, na.rm = TRUE), .groups = "drop")
  
  # save data to list
  karstula[[i]] <- df
}

karstula <- bind_rows(karstula)

# extract components from karstula$Scout.name
moisture_list_karstula <- karstula %>%
  mutate(
    point_prefix = str_extract(Scout.name, "^[^-]+-[0-9]+"),
    trenched_flag = case_when(
      str_ends(Scout.name, "T") ~ "True",
      str_ends(Scout.name, "C") ~ "False",
      TRUE ~ NA_character_
    )
  ) %>% # remove the trailing "-" from point_prefix to match db$point
  mutate(point_prefix = str_remove(point_prefix, "-")) %>% 
  select(point_prefix, trenched_flag, date, mean_value)

# separate db into Karstula and others based on condition
condition_karstula <- db$siteid %in% c("Karstula75", "Karstula76")

db_karstula <- db %>% filter(condition_karstula)

# join and update only the filtered part
# extract prefix from db$point for joining
db_karstula <- db_karstula %>%
  mutate(
    point_prefix = str_extract(point, "^[^_]+")
    ) %>%
  left_join(
    moisture_list_karstula,
    by = c("point_prefix", "trenched" = "trenched_flag", "date")
  ) %>%
  mutate(
    tsmoisture = if_else(is.na(tsmoisture) , mean_value, tsmoisture)
  ) %>%
  select(-mean_value, -point_prefix)


# ========
# Ränskälä
# ========

load("moisturedata/ränskälä/TMS4_data_RK_2020_2025.Rdata")

# add mean moisture per treatment
#moisture_ränskälä <- d.tw3 %>% # this data has the daily averages for each treatment
#  select(canopy, date, swc.mean) %>%
#  mutate(
#    canopy = if_else(
#      canopy == "CCF",
#      "Thinning",
#      canopy
#    )
#  )

# separate db into Ränskälä and others based on condition
condition_ränskälä <- db$siteid == "Ränskälänkorpi"

db_ränskälä <- db %>% filter(condition_ränskälä)

# check how many ränskälä plots match to db points
ränskälä_points <- unique(db_ränskälä$point)
d_points <- grep("^[0-9]+/.+", ränskälä_points, value = TRUE)
print(d_points)

# clean moisture data to have mean moisture per plot/date combo
moisture_ränskälä <- TMS4_data_RSK %>%
  select(Plot, Canopy_treatment, date, swc) %>%
  mutate(
    Canopy_treatment = case_when(
      Canopy_treatment == "CCF" ~ "Thinning",
      Canopy_treatment == "Non_harvested control" ~ "Control",
      TRUE ~ Canopy_treatment
    )
  ) %>%
  group_by(date, Plot, Canopy_treatment) %>%
  summarise(daily_mean_swc = mean(swc, na.rm = TRUE),
            .groups = "drop")

# Create a joining key for db_ränskälä
db_ränskälä <- db_ränskälä %>%
  mutate(key = trimws(point),
         key = case_when(
           grepl("^[0-9]+", key) ~ sub("^([0-9]+).*", "\\1", key),  # numeric prefix as string
           TRUE ~ key)
  )

# check how large proportion of moisture_ränskälä directly match with db_ränskälä
matches <- db_ränskälä$key %in% moisture_ränskälä$Plot
print(paste0("The fraction of observations that match moisture plots directly is: ",
             round(mean(matches), 4),
             ". And the total number of matches is: ",
             sum(matches)))

# join and update only the filtered part
# extract prefix from db$point for joining
db_ränskälä <- db_ränskälä %>%
  left_join(
    moisture_ränskälä,
    by = c("key" = "Plot", "date", "treatment" = "Canopy_treatment")
  ) %>%
  mutate(
    tsmoisture = coalesce(tsmoisture, daily_mean_swc)) %>%
  select(-daily_mean_swc, -key)

print(mean(!is.na(db_ränskälä$tsmoisture)))

# =======
# URUGUAY
# =======
rdb <- read.csv("moisturedata/uruguay/resp_data_rdb.csv", sep = ";", header = TRUE)
hist(rdb$soil_moisture)
# add moisture
moisture_uruguay <- rdb %>%
  select(tube.number, Date, pos, Mod, soil_moisture, T1_belowgr) %>%
  mutate(Date = as.Date(Date, format = "%m/%d/%Y"),
         tube.number = as.character(tube.number),
         trenched = case_when(
           pos == "Out" ~ "False",
           pos == "In" ~ "True",
           TRUE ~ NA_character_
         ),
         details = case_when(
           Mod == "CN" ~ "Natural Pasture",
           Mod == "Fbt" ~ "Forest Between Row",
           Mod == "Fin" ~ "Forest In Row",
           TRUE ~ NA_character_
         )
  ) %>%
  select(-Mod, -pos)

# separate db into uruguayin and others based on condition
condition_uruguay <- db$siteid == "RincondelBatovi"

db_uruguay <- db %>% filter(condition_uruguay)


# CHecking
tubet <- as.character(unique(rdb$tube.number))
sum(db_uruguay$point %in% tubet) / dim(db_uruguay)[1] # How many of the observations are in tube points
# temp
summary(db_uruguay$t10); summary(db_uruguay$t05); summary(db_uruguay$t30) # check how many temp are included
# we also need to add temperature

# Check for duplicates in each dataset
db_uruguay %>%
  count(point, date, trenched, j_flux) %>% # how many duplicates with same point/date/trenched/flux combo
  filter(n > 1)
moisture_uruguay %>%
  mutate(soil_moisture = round(soil_moisture, 4)) %>%
  count(tube.number, Date, trenched) %>%  # how many duplicates with same point/date/trenched combo
  filter(n > 1)

# LETS CLEAR DUPLICATES AND AGGREGATE

dup_keys <- moisture_uruguay %>%
  count(tube.number, Date, trenched) %>%
  filter(n > 1) %>%
  select(tube.number, Date, trenched)

# Separate rows with true identical and ones with different values
# rows that share same moist/temp
identical_rows <- moisture_uruguay %>%
  semi_join(dup_keys, by = c("tube.number", "Date", "trenched")) %>%
  group_by(tube.number, Date, trenched, soil_moisture, T1_belowgr) %>%
  filter(n() > 1) %>%
  ungroup

# Rows where duplicates have different moisture/temp (conflicts)
conflicting_rows <- moisture_uruguay %>%
  semi_join(dup_keys, by = c("tube.number", "Date", "trenched")) %>%
  group_by(tube.number, Date, trenched) %>%
  filter(n_distinct(soil_moisture) > 1 | n_distinct(T1_belowgr) > 1) %>%
  ungroup()

# print to inspect
identical_rows %>%
  arrange(tube.number, Date, trenched) %>%
  print(n = Inf)
conflicting_rows %>%
  arrange(tube.number, Date, trenched) %>%
  print(n = Inf)

# Collapse duplicate rows
moisture_uruguay <- moisture_uruguay %>%
  group_by(tube.number, Date, trenched) %>%
  summarise(
    soil_moisture = if_else(
      n_distinct(soil_moisture) == 1, # identical moistures?
      first(soil_moisture), # yes -> take any (first)
      mean(soil_moisture, na.rm = TRUE) # no -> take mean
    ),
    T1_belowgr = if_else(
      n_distinct(T1_belowgr) == 1,
      first(T1_belowgr),
      mean(T1_belowgr, na.rm = TRUE)
    ),
    .groups = "drop"
  )

# Check duplicate rows again to confirm succesful collapsing
moisture_uruguay %>%
  mutate(soil_moisture = round(soil_moisture, 4)) %>%
  count(tube.number, Date, trenched) %>%  # how many duplicates with same point/date/trenched combo
  filter(n > 1)

# JOINING
db_uruguay <- db_uruguay %>%
  left_join(
    moisture_uruguay,
    by = c("point" = "tube.number", "date" = "Date", "trenched")
  ) %>%
  mutate(
    tsmoisture = if_else(is.na(tsmoisture) , soil_moisture * 100, tsmoisture),
    t05 = if_else(is.na(t05), T1_belowgr, t05) # assumed that TOMST measures temperature at 5cm depth
  ) %>%
  select(-soil_moisture, -T1_belowgr)

hist(db_uruguay$tsmoisture)

# ===========
# SAINT MITRE
# ===========
# separate db into saintmitre and others based on condition
condition_sm <- db$siteid == "Saint Mitre"

db_sm <- db %>% filter(condition_sm)
db_sm$point <- as.integer(db_sm$point)

# check
table_counts <- table(db_sm$point, db_sm$treatment)
rowSums(table_counts > 0) > 1
print(table_counts)

table_subsite <- table(db_sm$point, db_sm$subsiteid)
print(table_subsite)
colnames(table_subsite) <- c("ht_uv", "ht_nuv", "ht_t", "mt_uv", "mt_nuv", "mt_t", "nt_nuv", "nt_t")
print(table_subsite)

## ==================================
#library(rlang)
## The points are in wrong subsiteids
#sm_treatments <- unique(db_sm$subsiteid)
#print(sm_treatments)
#
#assign(sm_treatments[1], c(1:4, 41:44, 53:56, 93:96))
#assign(sm_treatments[2], c(5:8, 45:48, 57:60, 97:100))
#assign(sm_treatments[3], c(9:12, 49:52, 61:64, 101:104))
#
#assign(sm_treatments[4], c(13:16, 65:68, 117:120, 105:108))
#assign(sm_treatments[5], c(17:20, 69:72, 121:124, 109:112))
#assign(sm_treatments[6], c(21:24, 73:76, 125:128, 113:116))
#
#assign(sm_treatments[7], c(25:28, 33:36, 77:80, 85:88))
#assign(sm_treatments[8], c(29:32, 37:40, 81:84, 89:92))
#
## ==================================

# NEXT IS FROM THE RAW DATA FILES
#sm_covariates <- read.csv("moisturedata/saint_mitre/saint_mitre_combined.csv", header = TRUE)
#sm_covariates <- sm_covariates[, c("Plot_No", "Date", "Time", "Tsoil", "Tair", "Msoil")]

## Check structure
#unique(db_sm$point); unique(sm_covariates$Plot_No)
#print(sum(sm_covariates$Plot_No %in% c(555, 666)))
#print(sum(!sm_covariates$Plot_No %in% unique(db_sm$point)))

#db_sm %>% # how many duplicate rows in dataset with same point/date/airtemp = 0
#  count(point, date, airtemp) %>%
#  filter(n > 1)

#sm_covariates %>% # how many duplicate rows in moisture data with same point/date = many
#  count(Plot_No, Date) %>%
#  filter(n > 1)

#sm_covariates <- sm_covariates %>% # transform date to same format
#  mutate(Date = dmy(Date))

## check these duplicate rows
#sm_covariates %>% 
#  group_by(Plot_No, Date) %>%
#  summarise(n = n(), .groups = "drop") %>%
#  filter(n > 1) %>%
#  print(n = 104)

## create a duplicate dataframe with duplicates diffference to group mean
#df_with_diff <- sm_covariates %>%
#  group_by(Plot_No, Date) %>%
#  filter(n() > 1) %>%
#  mutate(
#    Tsoil_mean = mean(Tsoil, na.rm = TRUE),
#    Tair_mean  = mean(Tair,  na.rm = TRUE),
#    Msoil_mean = mean(Msoil, na.rm = TRUE),
#    Tsoil_diff = Tsoil - Tsoil_mean,
#    Tair_diff  = Tair  - Tair_mean,
#    Msoil_diff = Msoil - Msoil_mean
#  ) %>%
#  ungroup() %>%
#  arrange(Plot_No, Date)

#print(df_with_diff, n = 218)

## Join unique (plot, date) rows normally, then join duplicates separately
## count how many rows per date + plot in sm_covariates
#sm_covariates_counts <- sm_covariates %>%
#  group_by(Date, Plot_No) %>%
#  summarise(n_rows = n(), .groups = "drop")

## add a flag if sm_covariates has duplicates for that date + plot
#db_sm_flagged <- db_sm %>%
#  left_join(sm_covariates_counts, by = c("date" = "Date", "point" = "Plot_No"))
#
#db_sm_unique <- db_sm_flagged %>% filter(n_rows == 1) # safe
#db_sm_dup <- db_sm_flagged %>% filter(n_rows > 1) # need fuzzy join
#
## Join the unique ones normally
#db_sm_unique_joined <- db_sm_unique %>%
#  left_join(sm_covariates, by = c("date" = "Date", "point" = "Plot_No"))

## fuzzy join
## here for each row in db_sm_dup, we look at all matching (date, plot) rows in sm_covariates
## and compute absolute difference in Airtemp and pick the row with minimum difference
## Airtemp2 is matched value from sm_covariates
#db_sm_dup_joined <- db_sm_dup %>%
#  rowwise() %>%
#  mutate(
#    # calculate difference between df1 airtemp and all df2 airtemps for the same date + plot
#    closest_row_index = which.min(abs(sm_covariates$Tair[sm_covariates$Date == date & sm_covariates$Plot_No == point] - airtemp))
#  ) %>%
#  mutate(
#    t05 = sm_covariates$Tsoil[sm_covariates$Date == date & sm_covariates$Plot_No == point][closest_row_index],
#    tsmoisture = sm_covariates$Msoil[sm_covariates$Date == date & sm_covariates$Plot_No == point][closest_row_index],
#    airtemp2 = sm_covariates$Tair[sm_covariates$Date == date & sm_covariates$Plot_No == point][closest_row_index]
#  ) %>%
#  ungroup() 

## Lets inspect differences in airtemp
#mad1 <- mean(abs(db_sm_dup_joined$airtemp - db_sm_dup_joined$airtemp2), na.rm = TRUE)
#cat(paste0("Fuzzy joined duplicate date/plot combos, unique for date/plot/airtemp (n=", nrow(db_sm_dup_joined), "). This join has mean absolute difference in airtemp: ", round(mad1, 2)))
#hist(db_sm_dup_joined$tsmoisture)
#f0m1 <- mean(round(db_sm_dup_joined$tsmoisture, 2) == 0.00)
#cat(paste0("Fuzzy joined duplicate date/plot combos, unique for date/plot/airtemp. Fraction of moisture values that are 0: ", round(f0m1,2 )))

#mad2 <- mean(abs(db_sm_unique_joined$airtemp - db_sm_unique_joined$Tair), na.rm = TRUE)
#cat(paste0("Normally joined unique plot/date combos (n=", nrow(db_sm_unique_joined), "). This join has mean absolute difference in airtemp: ", round(mad2, 2)))
#hist(db_sm_unique_joined$Msoil)
#f0m2 <- mean(round(db_sm_unique_joined$Msoil, 2) == 0.00)
#cat(paste0("Normally joined unique plot/date combos. Fraction of moisture values that are 0: ", round(f0m2,2 )))


# Join together
#db_sm_unique_joined <- db_sm_unique_joined %>%
#  mutate(
#    airtemp = coalesce(Tair, airtemp), # prioritise joined airtemp
#    tsmoisture = coalesce(Msoil, tsmoisture), # prioritise joined soil moisture
#    t05 = coalesce(Tsoil, t05) # prioritise joined soil temp
#  ) %>%
#  select(-Tair, -Msoil, -Tsoil, -Time, -n_rows)

#db_sm_dup_joined <- db_sm_dup_joined %>%
#  mutate(airtemp = coalesce(airtemp2, airtemp)) %>% # prioritise joined air temp
#  select(-closest_row_index, -n_rows, -airtemp2)

#db_sm_final <- bind_rows(db_sm_unique_joined, db_sm_dup_joined) %>%
#  mutate(point = as.character(point)) %>%
#  arrange(row_id)

#hist(db_sm_final$tsmoisture)


# NEXT IS FROM THE COMPILED DATA FORMAT FROM CHARLOTTE
# COLUMNS MESSED UP & END START LINES EVERYWHERE

# Load st mitre covariate data
sm_data <- read.csv("moisturedata/saint_mitre/St_Mitre_soil_respiration_SM_ST_CBok.csv", header = TRUE)

# Check structure
unique(db_sm$point);unique(sm_data$Monitoring.point.ID); unique(sm_data$Plot_No)
print(sum(sm_data$Plot_No %in% c(129, 130, 131, 610, 555, 666)))
print(sum(!sm_data$Monitoring.point.ID %in% unique(db_sm$point)))
table(sm_data$Monitoring.point.ID, sm_data$plot)
table(sm_data$Plot_No, sm_data$plot)
sum(is.na(sm_data$Monitoring.point.ID))


# HERE WE CHANGED $Plot_No to $Monitoring.point.ID
# filter out points based on db_sm (omit points 555 and 666 from moisture_sm)
condition_sm_points <- sm_data$Monitoring.point.ID %in% unique(db_sm$point)

moisture_sm <- sm_data %>%
  select(Monitoring.point.ID, corrected_date, Sub.site.ID, Tsoil, Msoil, Tair) %>%
  filter(condition_sm_points) %>%
  mutate(corrected_date = as.Date(corrected_date, format = "%d-%m-%Y"))

# Check for duplicate keys
db_sm %>%
  count(point, date, subsiteid) %>%
  filter(n > 1)

moisture_sm %>%
  count(Monitoring.point.ID, corrected_date, Sub.site.ID) %>%
  filter(n > 1)

# check these duplicate rows
moisture_sm %>%
  mutate(row_number = row_number()) %>%       # add row numbers
  group_by(Monitoring.point.ID, corrected_date, Sub.site.ID) %>%
  filter(n() > 1) %>%
  ungroup()

db_sm %>%
  group_by(point, date, subsiteid) %>%
  filter(n() > 1) %>%
  ungroup()

# Join moisture and temperature data with db_sm
db_sm <- db_sm %>%
  left_join(moisture_sm,
            by = c("point" = "Monitoring.point.ID",
                   "date" = "corrected_date",
                   "subsiteid" = "Sub.site.ID")
            ) %>%
  mutate(t05 = coalesce(t05, Tsoil),
         tsmoisture = coalesce(tsmoisture, Msoil),
         point = as.character(point),
         airtemp = coalesce(airtemp, Tair)
         ) %>%
  select(-Tsoil, -Msoil, -Tair)

# ======================================
# COMBINE KARSTULA AND RÄNSKÄLÄ AND REST
# ======================================

db_rest <- db %>% filter(!condition_karstula & !condition_ränskälä & !condition_uruguay & !condition_sm)

db_updated <- bind_rows(db_karstula, db_ränskälä, db_uruguay, db_sm, db_rest) %>%
  arrange(row_id) %>%
  select(-row_id) # keep original order of rows

# check moisture distribution table again
print("Moisture distribution table after adding covariates")
db_updated %>%
  group_by(siteid) %>%
  summarise(
    min = min(tsmoisture, na.rm = TRUE),
    max = max(tsmoisture, na.rm = TRUE),
    mean = mean(tsmoisture, na.rm = TRUE),
    n = n()
  ) %>%
  arrange(desc(max))


# ===========================================
# Rescale moisture levels for the Netherlands
# ===========================================

db_updated <- db_updated %>%
  group_by(siteid) %>%
  group_modify(~ {
    if (all(is.na(.x$tsmoisture))) {
      .x # return unchanged
    } else if (max(.x$tsmoisture, na.rm = TRUE) <= 1) {
      .x$tsmoisture <- .x$tsmoisture * 100
      .x
    } else {
      .x # already in percent
    }
  }) %>%
  ungroup()

# check moisture distribution table again
print("Moisture distribution table after scalingto percentages")
db_updated %>%
  group_by(siteid) %>%
  summarise(
    min = min(tsmoisture, na.rm = TRUE),
    max = max(tsmoisture, na.rm = TRUE),
    mean = mean(tsmoisture, na.rm = TRUE),
    n = n()
  ) %>%
  arrange(desc(max))

# temp 05
print("Temperature at 5cm distribution table")
db_updated %>%
  group_by(siteid) %>%
  summarise(
    min = min(t05, na.rm = TRUE),
    max = max(t05, na.rm = TRUE),
    mean = mean(t05, na.rm = TRUE),
    n = n()
  ) %>%
  arrange(desc(max))

zero_counts <- tibble(
  variable = c("tsmoisture", "t05", "airtemp"),
  zeros = c(
    sum(db_updated$tsmoisture == 0, na.rm = TRUE),
    sum(db_updated$t05 == 0, na.rm = TRUE),
    sum(db_updated$airtemp == 0, na.rm = TRUE)
  ),
  NAs = c(
    sum(is.na(db_updated$tsmoisture)),
    sum(is.na(db_updated$t05 == 0)),
    sum(is.na(db_updated$airtemp == 0))
  ),
  nonNAs = c(
    sum(!is.na(db_updated$tsmoisture)),
    sum(!is.na(db_updated$t05 == 0)),
    sum(!is.na(db_updated$airtemp == 0))
))
paste("Table of covariate values")
print(zero_counts)

# =============================
# Remove 0 and negative values from moisture
# =============================
db_updated <- db_updated %>%
  mutate(
    tsmoisture = if_else(tsmoisture <= 0, NA_real_, tsmoisture)
  )

print("Moisture distribtion tabel after filtering out values <= 0")
# check moisture distribution table again
db_updated %>%
  group_by(siteid) %>%
  summarise(
    min = min(tsmoisture, na.rm = TRUE),
    max = max(tsmoisture, na.rm = TRUE),
    mean = mean(tsmoisture, na.rm = TRUE),
    n = n()
  ) %>%
  arrange(desc(max))

zero_counts <- tibble(
  variable = c("tsmoisture", "t05", "airtemp"),
  zeros = c(
    sum(db_updated$tsmoisture == 0, na.rm = TRUE),
    sum(db_updated$t05 == 0, na.rm = TRUE),
    sum(db_updated$airtemp == 0, na.rm = TRUE)
  ),
  NAs = c(
    sum(is.na(db_updated$tsmoisture)),
    sum(is.na(db_updated$t05 == 0)),
    sum(is.na(db_updated$airtemp == 0))
  ),
  nonNAs = c(
    sum(!is.na(db_updated$tsmoisture)),
    sum(!is.na(db_updated$t05 == 0)),
    sum(!is.na(db_updated$airtemp == 0))
  ))
paste("Table of covariate values after 0 removal in moisture")
print(zero_counts)

# =====================
# Save updated database
# =====================
# Combine Dumbravita and Karstula siteids
#db_updated <- db_updated %>%
#  mutate(
#    siteid = case_when(
#      siteid == "DumbravitaTrench" ~ "Dumbravita",
#      siteid %in% c("Karstula75", "Karstula76") ~ "Karstula",
#      TRUE ~ siteid
#    )
#  )

# remove j_ from colnames
colnames(db_updated) <- gsub("^j_", "", colnames(db_updated))

# remove pointtype column
db_updated <- db_updated %>%
  select(-pointtype)

# change empty character strings to NA
db_updated <- db_updated %>%
  mutate(across(where(is.character), ~ na_if(.x, "")))


# Add Country information
db_updated <- db_updated %>%
  mutate(country = case_when(
    siteid == "Dobroc" ~ "Slovakia",
    siteid == "Dumbravita" ~ "Romania",
    siteid == "DumbravitaTrench" ~ "Romania",
    siteid == "Gamiz" ~ "Spain",
    siteid == "Karstula75" ~ "Finland",
    siteid == "Karstula76" ~ "Finland",
    siteid == "Kelheim-Parsberg" ~ "Germany",
    siteid == "Kranzberg-Freising" ~ "Germany",
    siteid == "Kroondomein" ~ "Netherlands",
    siteid == "Zwolse Bos" ~ "Netherlands",
    siteid == "NP Hoge Veluwe" ~ "Netherlands",
    siteid == "Llobera" ~ "Spain",
    siteid == "Ränskälänkorpi" ~ "Finland",
    siteid == "Saint Mitre" ~ "France",
    siteid == "Secanella" ~ "Spain",
    siteid == "St Christol" ~ "France",
    siteid == "Wasserburg-Maitenbeth" ~ "Germany",
    siteid == "RincondelBatovi" ~ "Uruguay",
    siteid == "Kacergine" ~ "Lithuania",
    TRUE ~ NA_character_
    ), .before = date
  )

write.csv(db_updated, file = "holisoils_updated.csv", row.names = FALSE)


## ========================================
## Exploring Ränskälänkorpi sites and plots
## ========================================
# char_vec <- unique(db_ränskälä[db_ränskälä$subsiteid == "Ditch", "point"])
# print(char_vec[order(as.numeric(char_vec))])

print("Script run succesfully")