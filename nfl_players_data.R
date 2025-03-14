library(tidyverse)
library(ggrepel)
library(nflreadr)
# load data from season 2018 to season 2023, considering the player's career length and stability of player performance over time.
years <- 2018:2023
pbp_data <- map_dfr(years, load_pbp)
# qb data yearly
qb_stats_yearly <- pbp_data %>%
  filter(pass_attempt == 1) %>%
  group_by(season, id,passer) %>%
  summarize(
    pass_attempts = n(),
    completions = sum(complete_pass, na.rm = TRUE),
    passing_yards = sum(yards_gained, na.rm = TRUE),
    touchdowns = sum(pass_touchdown, na.rm = TRUE),
    interceptions = sum(interception, na.rm = TRUE),
    total_epa = sum(epa, na.rm = TRUE),
    avg_epa = mean(epa, na.rm = TRUE),
    cpoe = mean(cpoe, na.rm = TRUE)
  ) %>%
  arrange(season, desc(total_epa))

head(qb_stats_yearly)

# rb data yearly
rb_stats_yearly <- pbp_data %>%
  filter(rush_attempt == 1) %>%
  group_by(season, id, rusher) %>%
  summarize(
    rush_attempts = n(),
    rushing_yards = sum(yards_gained, na.rm = TRUE),
    touchdowns = sum(rush_touchdown, na.rm = TRUE),
    total_epa = sum(epa, na.rm = TRUE),
    avg_epa = mean(epa, na.rm = TRUE)
  ) %>%
  arrange(season, desc(rushing_yards))
head(rb_stats_yearly)

# wr/te data yearly
wr_stats_yearly <- pbp_data %>%
  filter(pass_attempt == 1, !is.na(receiver)) %>%
  group_by(season, id, receiver) %>%
  summarize(
    targets = n(),
    receptions = sum(complete_pass, na.rm = TRUE),
    receiving_yards = sum(yards_gained, na.rm = TRUE),
    touchdowns = sum(pass_touchdown, na.rm = TRUE),
    total_epa = sum(epa, na.rm = TRUE),
    avg_epa = mean(epa, na.rm = TRUE)
  ) %>%
  arrange(season,desc(receiving_yards))

head(wr_stats_yearly)

