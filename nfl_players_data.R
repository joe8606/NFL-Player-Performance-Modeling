library(tidyverse)
library(ggrepel)
library(nflreadr)
library(nflfastR)
library(dplyr)
years <- 2018:2023
# codes that obtain play by play data, keep for record
pbp_data <- load_pbp(years)
# write.csv(pbp_data, "C:/Users/Katrina/Desktop/CYang Rutgers/data/pbp_data.csv", row.names = FALSE)



# Get the roster data- NFL players's data
roster_data <- fast_scraper_roster(years)
# write.csv(roster_data, "roster.csv", row.names = FALSE)


  
# extract QB basic data
QB <- roster_data %>%
  filter(position == 'QB') %>%group_by(season, gsis_id)%>%
  select(season,gsis_id, full_name, team, position, birth_date, height, weight, years_exp, rookie_year,entry_year, draft_number,depth_chart_position)
# years_exp- experiences
# rookie_year:when the player plays in their first NFL game 
# entry_year:when the player is officially part of the league(drafted/signed)
# depth_chart_position:showing who is likely to start and who is a backup

# get QB gsis_id
QB_id <- QB %>%
  ungroup() %>%
  pull(gsis_id)
  
nextgen_passing <- load_nextgen_stats(
  seasons = TRUE,
  stat_type = 'passing',
  file_type = getOption("nflreadr.rds", default = "rds")
)
nextgen_passing <- nextgen_passing%>%
  select("season", "week", "avg_time_to_throw", "avg_completed_air_yards", "avg_intended_air_yards", "avg_air_yards_differential", "aggressiveness", "max_completed_air_distance", "avg_air_yards_to_sticks", "pass_yards", "pass_touchdowns", "interceptions", "completions", "completion_percentage", "expected_completion_percentage", "completion_percentage_above_expectation", "avg_air_distance", "max_air_distance", "player_gsis_id" )

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
    air_yards = sum(ifelse(complete_pass == 1, air_yards, 0), na.rm = TRUE),
    first_down_pass = sum(first_down_pass,na.rm = TRUE),
    rush_attempts = sum(rush_attempt, na.rm = TRUE),
    rushing_yards = sum(rushing_yards, na.rm = TRUE),
    rush_touchdowns = sum(rush_touchdown, na.rm = TRUE),
    first_down_rush = sum(first_down_rush, na.rm = TRUE),
    third_down_converted =sum(third_down_converted, na.rm = TRUE),
    third_down_failed =sum(third_down_failed, na.rm = TRUE),
    third_down_rate = third_down_converted/sum(third_down_converted,third_down_failed),
    fourth_down_converted =sum(fourth_down_converted, na.rm = TRUE),
    fourth_down_failed =sum(fourth_down_failed, na.rm = TRUE),
    fourth_down_rate = fourth_down_converted/sum(fourth_down_converted,fourth_down_failed),
    fumble = sum(fumble, na.rm = TRUE),
    fumble_forced = sum(fumble_forced, na.rm = TRUE),
    fumble_not_forced = sum(fumble_not_forced, na.rm = TRUE),
    tackled_for_loss = sum(tackled_for_loss, na.rm = TRUE),
    fumble_lost =sum(fumble_lost, na.rm = TRUE),
    sack = sum(sack, na.rm = TRUE),
    penalties = sum(ifelse(penalty_player_id %in% QB_id, penalty, 0), na.rm = TRUE),
    penalty_yards = sum(ifelse(penalty_player_id %in% QB_id, penalty_yards, 0), na.rm = TRUE),
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

qb_stats <- merge(qb_stats, nextgen_passing, by.x = c("season","week", "gsis_id"), by.y = c("season","week", "player_gsis_id"),  all.x = TRUE)



# Get RB basic data
RB <- roster_data %>%
  filter(position == 'RB') %>%
  group_by(season, gsis_id)%>%
  select(season,gsis_id, full_name, team, position, birth_date, height, weight, years_exp, rookie_year,entry_year, draft_number,depth_chart_position)

# get RB gsis_id
RB_id <-RB %>%
  ungroup() %>%
  pull(gsis_id)

nextgen_rushing<- load_nextgen_stats(
  seasons = TRUE,
  stat_type = 'rushing',
  file_type = getOption("nflreadr.rds", default = "rds")
)

nextgen_rushing <- nextgen_rushing%>%
  select('season','week',"efficiency","percent_attempts_gte_eight_defenders","avg_time_to_los","rush_attempts","rush_yards", "avg_rush_yards", "rush_touchdowns", "player_gsis_id" ,"expected_rush_yards","rush_yards_over_expected","rush_yards_over_expected_per_att","rush_pct_over_expected" )


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
    first_down_rush = sum(first_down_rush, na.rm = TRUE),
    targets = sum(pass_attempt, na.rm = TRUE),
    receptions = sum(complete_pass, na.rm = TRUE),
    yac = sum(yards_after_catch, na.rm = TRUE),
    # yards after catch
    first_down_pass = sum(first_down_pass,na.rm = TRUE),
    third_down_converted =sum(third_down_converted, na.rm = TRUE),
    third_down_failed =sum(third_down_failed, na.rm = TRUE),
    third_down_rate = third_down_converted/sum(third_down_converted,third_down_failed),
    fourth_down_converted =sum(fourth_down_converted, na.rm = TRUE),
    fourth_down_failed =sum(fourth_down_failed, na.rm = TRUE),
    fourth_down_rate = fourth_down_converted/sum(fourth_down_converted,fourth_down_failed),
    fumble = sum(fumble, na.rm = TRUE),
    fumble_forced = sum(fumble_forced, na.rm = TRUE),
    fumble_not_forced = sum(fumble_not_forced, na.rm = TRUE),
    fumble_lost =sum(fumble_lost, na.rm = TRUE),
    tackled_for_loss = sum(tackled_for_loss, na.rm = TRUE),
    penalties = sum(ifelse(penalty_player_id %in% RB_id, penalty, 0), na.rm = TRUE),
    penalty_yards = sum(ifelse(penalty_player_id %in% RB_id, penalty_yards, 0), na.rm = TRUE),
    total_epa = sum(epa, na.rm = TRUE),
    avg_epa = mean(epa, na.rm = TRUE),
    .groups = 'keep'
  ) %>%
  arrange(season)

# merge RB basic data and play data
rb_stats <- merge(RB, rb_play_stats, by.x = c("season", "gsis_id"), by.y = c("season", "player_id"),  all = FALSE)%>%relocate(week, .after = season)
rb_stats <- merge(rb_stats, nextgen_rushing, by.x = c("season","week", "gsis_id"), by.y = c("season","week", "player_gsis_id"),  all.x = TRUE)


# wr/te data
# Get wr/te basic data
wrte <- roster_data %>%
  filter(position == 'TE'|position == 'WR') %>%
  group_by(season, gsis_id)%>%
  select(season,gsis_id, full_name, team, position, birth_date, height, weight, years_exp, rookie_year,entry_year, draft_number,depth_chart_position)

# get wr/te gsis_id
wrte_id <- wrte %>%
  ungroup()%>%
  pull(gsis_id)

nextgen_receiving<- load_nextgen_stats(
  seasons = TRUE,
  stat_type = 'receiving',
  file_type = getOption("nflreadr.rds", default = "rds")
)

nextgen_receiving <- nextgen_receiving%>%
  select('season','week',"avg_cushion","avg_separation","avg_intended_air_yards","percent_share_of_intended_air_yards","receptions","targets", "catch_percentage","rec_touchdowns" ,"avg_yac", "avg_expected_yac", "avg_yac_above_expectation","player_gsis_id" )

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
    air_yards = sum(ifelse(complete_pass == 1, air_yards, 0), na.rm = TRUE),
    yac = sum(yards_after_catch, na.rm = TRUE),
    first_down_receive = sum(first_down_pass,na.rm = TRUE),
    rush_attempts = sum(rush_attempt, na.rm = TRUE),
    rushing_yards = sum(ifelse(play_type == 'run', yards_gained,0), na.rm = TRUE),
    rush_tds = sum(rush_touchdown, na.rm = TRUE),
    first_down_rush = sum(first_down_rush, na.rm = TRUE),
    third_down_converted =sum(third_down_converted, na.rm = TRUE),
    third_down_failed =sum(third_down_failed, na.rm = TRUE),
    third_down_rate = third_down_converted/sum(third_down_converted,third_down_failed),
    fourth_down_converted =sum(fourth_down_converted, na.rm = TRUE),
    fourth_down_failed =sum(fourth_down_failed, na.rm = TRUE),
    fourth_down_rate = fourth_down_converted/sum(fourth_down_converted,fourth_down_failed),
    fumble = sum(fumble, na.rm = TRUE),
    fumble_forced = sum(fumble_forced, na.rm = TRUE),
    fumble_not_forced = sum(fumble_not_forced, na.rm = TRUE),
    fumble_lost =sum(fumble_lost, na.rm = TRUE),
    tackled_for_loss = sum(tackled_for_loss, na.rm = TRUE),
    penalties = sum(ifelse(penalty_player_id %in% wrte_id, penalty, 0), na.rm = TRUE),
    penalty_yards = sum(ifelse(penalty_player_id %in% wrte_id, penalty_yards, 0), na.rm = TRUE),
    total_epa = sum(epa, na.rm = TRUE),
    avg_epa = mean(epa, na.rm = TRUE),
    .groups = 'keep'
    ) %>%
    arrange(season)

# merge wrte basic data and play data
wrte_stats <- merge(wrte, wrte_play_stats, by.x = c("season", "gsis_id"), by.y = c("season", "player_id"),  all = FALSE)%>%relocate(week, .after = season)

wrte_stats <- merge(wrte_stats, nextgen_receiving, by.x = c("season","week", "gsis_id"), by.y = c("season","week", "player_gsis_id"),  all.x = TRUE)




