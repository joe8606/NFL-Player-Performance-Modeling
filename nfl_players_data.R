library(tidyverse)
library(ggrepel)
library(nflreadr)
library(nflfastR)
library(dplyr)
# load data from season 2018 to season 2023, considering the player's career length and stability of player performance over time.
years <- 2018:2023
pbp_data <- load_pbp(years)
roster_data <- fast_scraper_roster(years)
# extract QB basic data
QB <- roster_data %>%
  filter(position == 'QB') %>%group_by(season, gsis_id)%>%
  select(season,gsis_id, full_name, position, birth_date, height, weight, years_exp, rookie_year,entry_year, draft_number,depth_chart_position)
# years_exp- experiences
# rookie_year:when the player plays in their first NFL game 
# entry_year:when the player is officially part of the league(drafted/signed)
# depth_chart_position:showing who is likely to start and who is a backup

# get QB gsis_id
QB_id <- QB %>%
  ungroup() %>%
  pull(gsis_id)
  

qb_play_stats <- pbp_data %>%
  # Create a new column: player_id.Apply passer/rusher player IDs that are in QB_id to player_id
  mutate(
    passer_qb = if_else(passer_player_id %in% QB_id, passer_player_id, NA_character_),
    rusher_qb = if_else(rusher_player_id %in% QB_id, rusher_player_id, NA_character_),
    player_id = coalesce(passer_qb, rusher_qb)
  )%>%
  # Get rid of NA value
  filter(!is.na(player_id) )%>%
  group_by(season, week, player_id) %>%
  summarize(
    pass_attempts = sum(pass_attempt, na.rm = TRUE),
    completions = sum(complete_pass, na.rm = TRUE),
    comp_pct = pass_attempts/completions * 100,
    air_yards = sum(ifelse(complete_pass == 1, air_yards, 0), na.rm = TRUE),
    passing_yards = sum(ifelse(play_type == 'pass', yards_gained,0), na.rm = TRUE),
    pass_touchdowns = sum(pass_touchdown, na.rm = TRUE),
    interceptions = sum(interception, na.rm = TRUE),
    rush_attempts = sum(rush_attempt, na.rm = TRUE),
    rushing_yards = sum(rushing_yards, na.rm = TRUE),
    rush_touchdowns = sum(rush_touchdown, na.rm = TRUE),
    fumble = sum(fumble, na.rm = TRUE),
    sack = sum(sack, na.rm = TRUE),
    qb_dropback = sum(qb_dropback, na.rm = TRUE),
    # epa - expected points added (or lost) by plays
    total_epa = sum(epa, na.rm = TRUE), 
    avg_epa = mean(epa, na.rm = TRUE),
    # cpoe:a quarterback’s actual completion percentage to the expected completion percentage based on factors like pass depth, receiver separation, pressure, and field position.
    cpoe = mean(cpoe, na.rm = TRUE),
    .groups = 'keep'
  ) %>%
  arrange(season, week)

# merge QB basic data and play data, keep all the rows in qb_play_stats
qb_stats <- merge(QB, qb_play_stats, by.x = c("season", "gsis_id"), by.y = c("season", "player_id"),  all = FALSE) %>% relocate(week, .after = season)


write.csv(qb_stats,'C:/Users/Katrina/Desktop/CYang Rutgers/data/qb_stats.csv',row.names = FALSE)


# Get RB basic data
RB <- roster_data %>%
  filter(position == 'RB') %>%
  group_by(season, gsis_id)%>%
  select(season,gsis_id, full_name, position, birth_date, height, weight, years_exp, rookie_year,entry_year, draft_number,depth_chart_position)

# get RB gsis_id
RB_id <-RB %>%
  ungroup() %>%
  pull(gsis_id)

# Get RB 
rb_play_stats <- pbp_data %>%
  mutate(
    rusher_rb = if_else(rusher_player_id %in% RB_id, rusher_player_id, NA_character_),
    receiver_rb = if_else(receiver_player_id %in% RB_id, receiver_player_id, NA_character_),
    player_id = coalesce(rusher_rb, receiver_rb)
  )%>%
   # Get rid of NA value
  filter(!is.na(player_id) )%>%
  group_by(season, week, player_id) %>%
  summarize(
    rush_attempts = sum(rush_attempt,na.rm = TRUE),
    rushing_yards = sum(ifelse(play_type == 'run', yards_gained,0), na.rm = TRUE),
    rush_ypa = rushing_yards/rush_attempts * 100 , # Rushing Yards per Attempt 
    rush_tds = sum(rush_touchdown, na.rm = TRUE),
    receptions = sum(complete_pass, na.rm = TRUE),
    yac = sum(yards_after_catch, na.rm = TRUE), # yards after catch
    fumble = sum(fumble, na.rm = TRUE),
    targets = sum(pass_attempt, na.rm = TRUE),
    total_epa = sum(epa, na.rm = TRUE),
    avg_epa = mean(epa, na.rm = TRUE),
    .groups = 'keep'
  ) %>%
  arrange(season)

# merge RB basic data and play data
rb_stats <- merge(RB, rb_play_stats, by.x = c("season", "gsis_id"), by.y = c("season", "player_id"),  all = FALSE)%>%relocate(week, .after = season)

write.csv(rb_stats,'C:/Users/Katrina/Desktop/CYang Rutgers/data/rb_stats.csv',row.names = FALSE)

# wr/te data
# Get wr/te basic data
wrte <- roster_data %>%
  filter(position == 'TE'|position == 'WR') %>%
  group_by(season, gsis_id)%>%
  select(season,gsis_id, full_name, position, birth_date, height, weight, years_exp, rookie_year,entry_year, draft_number,depth_chart_position)

# get wr/te gsis_id
wrte_id <- wrte %>%
  ungroup()%>%
  pull(gsis_id)

wrte_play_stats <- pbp_data %>%
  mutate(
    receiver_wrte = if_else(receiver_player_id %in% wrte_id, receiver_player_id, NA_character_),
    rusher_wrte = if_else(rusher_player_id %in% wrte_id, rusher_player_id, NA_character_),
    player_id = coalesce(receiver_wrte, rusher_wrte)
  )%>%
  # Get rid of NA value
  filter(!is.na(player_id))%>%
  group_by(season, week, player_id)%>%
  summarize(
    targets = sum(pass_attempt, na.rm = TRUE),  
    receptions = sum(complete_pass, na.rm = TRUE),
    catch_rate = receptions/targets* 100,
    air_yards = sum(ifelse(complete_pass == 1, air_yards, 0), na.rm = TRUE),
    yac = sum(yards_after_catch, na.rm = TRUE),
    pass_tds = sum(pass_touchdown, na.rm = TRUE),
    rush_attempts = sum(rush_attempt, na.rm = TRUE),
    rushing_yards = sum(ifelse(play_type == 'run', yards_gained,0), na.rm = TRUE),
    rush_tds = sum(rush_touchdown, na.rm = TRUE),
    fumble = sum(fumble, na.rm = TRUE),
    total_epa = sum(epa, na.rm = TRUE),
    avg_epa = mean(epa, na.rm = TRUE),
    .groups = 'keep'
    ) %>%
    arrange(season)

# merge wrte basic data and play data
wrte_stats <- merge(wrte, wrte_play_stats, by.x = c("season", "gsis_id"), by.y = c("season", "player_id"),  all = FALSE)%>%relocate(week, .after = season)
