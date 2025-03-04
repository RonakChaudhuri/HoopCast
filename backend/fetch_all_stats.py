import time
import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.static import players
from database import get_connection
from psycopg2.extras import RealDictCursor

def insert_current_season_stats(player_id, season, adv_stats, trad_stats):
    """
    Insert or update current season stats for a given player.
    adv_stats: dict with keys: OFF_RATING, DEF_RATING, TS_PCT, USG_PCT, EFG_PCT, PIE
    trad_stats: dict with keys: PTS, REB, AST
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        query = """
            INSERT INTO current_season_stats
                (player_id, season, off_rating, def_rating, ts_pct, usg_pct, efg_pct, pie, pts, reb, ast)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (player_id, season)
            DO UPDATE SET
                off_rating = EXCLUDED.off_rating,
                def_rating = EXCLUDED.def_rating,
                ts_pct = EXCLUDED.ts_pct,
                usg_pct = EXCLUDED.usg_pct,
                efg_pct = EXCLUDED.efg_pct,
                pie = EXCLUDED.pie,
                pts = EXCLUDED.pts,
                reb = EXCLUDED.reb,
                ast = EXCLUDED.ast;
        """
        cur.execute(query, (
            player_id,
            season,
            adv_stats.get('OFF_RATING'),
            adv_stats.get('DEF_RATING'),
            adv_stats.get('TS_PCT'),
            adv_stats.get('USG_PCT'),
            adv_stats.get('EFG_PCT'),
            adv_stats.get('PIE'),
            trad_stats.get('PTS'),
            trad_stats.get('REB'),
            trad_stats.get('AST')
        ))
        conn.commit()
        print(f"Inserted/Updated stats for player_id {player_id} for season {season}.")
    except Exception as e:
        conn.rollback()
        print("Error inserting/updating stats for player_id", player_id, ":", e)
    finally:
        cur.close()
        conn.close()

def get_player_id(full_name):
    """
    Retrieves the internal player_id from your local players table given the full_name.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT player_id FROM players WHERE full_name = %s;", (full_name,))
        result = cur.fetchone()
        if result:
            return result[0]
        else:
            return None
    finally:
        cur.close()
        conn.close()

def fetch_all_current_season_stats():
    season = "2024-25"
    
    # Retrieve league-wide advanced stats (Per36) for the current season
    advanced_stats = leaguedashplayerstats.LeagueDashPlayerStats(
        measure_type_detailed_defense='Advanced',
        per_mode_detailed='Per36',
        season=season
    )
    df_adv = advanced_stats.get_data_frames()[0]
    
    # Retrieve league-wide traditional stats (Per36) for the current season
    traditional_stats = leaguedashplayerstats.LeagueDashPlayerStats(
        per_mode_detailed='Per36',
        season=season
    )
    df_trad = traditional_stats.get_data_frames()[0]
    
    # Get a list of current active players
    active_players = players.get_active_players()
    total = len(active_players)
    print(f"Found {total} active players.")
    
    # Define the columns we need from the advanced and traditional DataFrames
    adv_columns = ['PLAYER_NAME', 'OFF_RATING', 'DEF_RATING', 'TS_PCT', 'USG_PCT', 'EFG_PCT', 'PIE']
    trad_columns = ['PLAYER_NAME', 'PTS', 'REB', 'AST']
    
    processed_count = 0
    for player in active_players:
        full_name = player.get("full_name")
        
        # Filter advanced stats for this player
        adv_row = df_adv[df_adv['PLAYER_NAME'] == full_name]
        # Filter traditional stats for this player
        trad_row = df_trad[df_trad['PLAYER_NAME'] == full_name]
        
        if not adv_row.empty and not trad_row.empty:
            adv_stats = adv_row[adv_columns].iloc[0].to_dict()
            trad_stats = trad_row[trad_columns].iloc[0].to_dict()
            
            # Retrieve the internal player_id from your local database
            internal_id = get_player_id(full_name)
            if internal_id:
                insert_current_season_stats(internal_id, season, adv_stats, trad_stats)
                processed_count += 1
            else:
                print(f"Player {full_name} not found in local database.")
        else:
            print(f"Stats not found for {full_name}.")
        
        # Optional: slight delay between players
        time.sleep(0.2)
    
    print(f"Processed stats for {processed_count} players.")

if __name__ == "__main__":
    fetch_all_current_season_stats()
