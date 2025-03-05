from nba_api.stats.endpoints import leaguedashplayerstats
from database import get_connection
import time

def fetch_and_store_traditional_stats(season="2024-25"):
    # Retrieve traditional stats in PerGame mode for the current season.
    # The default measure type is usually "Traditional".
    traditional = leaguedashplayerstats.LeagueDashPlayerStats(
        per_mode_detailed="PerGame",
        season=season
    )
    df = traditional.get_data_frames()[0]
    print("Fetched traditional stats for", len(df), "players.")

    # Iterate over each row in the DataFrame.
    for index, row in df.iterrows():
        player_name = row["PLAYER_NAME"]
        pts = row["PTS"]
        ast = row["AST"]
        reb = row["REB"]
        stl = row["STL"]
        blk = row["BLK"]
        fg_pct = row["FG_PCT"]
        fg3_pct = row["FG3_PCT"]
        ft_pct = row["FT_PCT"]

        # Look up the player's internal ID in your players table.
        conn = get_connection()
        cur = conn.cursor()
        try:
            # Use a partial match with unaccent so that diacritics are ignored.
            search_param = f"%{player_name}%"
            cur.execute("""
                SELECT player_id FROM players
                WHERE unaccent(full_name) ILIKE unaccent(%s)
                LIMIT 1;
            """, (search_param,))
            result = cur.fetchone()
            if result:
                player_id = result[0]
                # Insert or update the traditional stats in the database.
                cur.execute("""
                    INSERT INTO traditional_stats 
                      (player_id, season, pts_per_game, ast_per_game, reb_per_game, stl_per_game, blk_per_game, fg_pct, fg3_pct, ft_pct)
                    VALUES 
                      (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (player_id, season)
                    DO UPDATE SET 
                      pts_per_game = EXCLUDED.pts_per_game,
                      ast_per_game = EXCLUDED.ast_per_game,
                      reb_per_game = EXCLUDED.reb_per_game,
                      stl_per_game = EXCLUDED.stl_per_game,
                      blk_per_game = EXCLUDED.blk_per_game,
                      fg_pct = EXCLUDED.fg_pct,
                      fg3_pct = EXCLUDED.fg3_pct,
                      ft_pct = EXCLUDED.ft_pct;
                """, (player_id, season, pts, ast, reb, stl, blk, fg_pct, fg3_pct, ft_pct))
                conn.commit()
                print(f"Inserted/Updated traditional stats for {player_name} (player_id: {player_id})")
            else:
                print(f"Player not found locally for {player_name}")
        except Exception as e:
            conn.rollback()
            print("Error inserting stats for", player_name, ":", e)
        finally:
            cur.close()
            conn.close()
        time.sleep(0.1)  # Optional delay to be courteous to the API

if __name__ == "__main__":
    fetch_and_store_traditional_stats()
