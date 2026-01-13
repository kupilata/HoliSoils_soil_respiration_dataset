library(dplyr)
library(ggplot2)
setwd("/scratch/project_2010938/Taavi_new")

df <- read.csv("holisoils_updated.csv", header = TRUE, check.names = FALSE)

# Moisture distributions
par(mfrow = c(1,1))
for (site in unique(df$siteid)) {
  df_subset <- df[df$siteid == site, ]
  
  # Skip sites with no valid moisture data
  if (all(is.na(df_subset$tsmoisture))) {
    print(paste0("Skipping ", site))
    next
  }
  
  print(
    ggplot(df_subset, aes(tsmoisture)) +
      geom_density() +
      labs(x = "Moisture in SWC %",
           y = "density",
           title = paste0("Distribution of moisture in ", site)) +
      annotate(
        "label",
        x = Inf,
        y = Inf,
        label = paste0(paste0("% NAs: ", round(mean(is.na(df_subset$tsmoisture)) * 100, 1)),
                       "\n",
                       paste0("0 values: ", sum(df_subset$tsmoisture == 0, na.rm = TRUE)),
                       "\n",
                       paste0("n = ", length(df_subset$tsmoisture))),
        hjust = 1,      # horizontal justification (1 = right)
        vjust = 1,      # vertical justification (1 = top)
        fill = "white", 
        color = "black"
      ) +
      theme_minimal()
  )
}


df_uruguay <- df[df$siteid == "RincondelBatovi", ]
ggplot(df_uruguay, aes(date, tsmoisture)) +
  geom_line() +
  labs(x = "date",
       y = "moisture",
       title = "timeseries of moisture in Uruguary") +
  theme_minimal()

df_kranzberg <- df[df$siteid == "Kranzberg-Freising", ]
ggplot(df_kranzberg, aes(tsmoisture)) +
  geom_density() +
  labs(x = "moisture",
       y = "density",
       title = "Kranzberg-Freising") +
  theme_minimal()

sum(is.na(df_kranzberg$tsmoisture))
