from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd

# Retrieve league-wide advanced stats in Per36 mode for the current season
advanced_stats = leaguedashplayerstats.LeagueDashPlayerStats(
    measure_type_detailed_defense='Advanced',
    per_mode_detailed='Per36',
    season="2024-25"
)

# Get the data as a DataFrame
df_adv = advanced_stats.get_data_frames()[0]

# Filter the DataFrame for LeBron James
lebron_stats = df_adv[df_adv['PLAYER_NAME'] == "LeBron James"]

# Select the columns of interest: Offense Rating, Defense Rating, TS%, Usage%, eFG%, and PIE
columns_of_interest = ['PLAYER_NAME', 'OFF_RATING', 'DEF_RATING', 'TS_PCT', 'USG_PCT', 'EFG_PCT', 'PIE']
lebron_selected_stats = lebron_stats[columns_of_interest]

print(lebron_selected_stats)

# Retrieve league-wide traditional stats in Per36 mode for the current season
traditional_stats = leaguedashplayerstats.LeagueDashPlayerStats(
    per_mode_detailed='Per36',
    season="2024-25"
)

# Get the data as a DataFrame
df_trad = traditional_stats.get_data_frames()[0]

# Filter the DataFrame for LeBron James
lebron_trad_stats = df_trad[df_trad['PLAYER_NAME'] == "LeBron James"]

# Select and print the relevant columns:
# PTS (points per 36), REB (rebounds per 36), AST (assists per 36)
columns_of_interest = ['PLAYER_NAME', 'PTS', 'REB', 'AST']
print(lebron_trad_stats[columns_of_interest])

