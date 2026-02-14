import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.static import players as nba_players
from database import get_connection
from psycopg2.extras import execute_batch


def _null_if_nan(value):
    return None if pd.isna(value) else value


def _player_id_map(conn):
    cur = conn.cursor()
    try:
        cur.execute("SELECT nba_player_id, player_id FROM players;")
        return {int(nba_id): int(player_id) for nba_id, player_id in cur.fetchall()}
    finally:
        cur.close()


def _active_nba_player_ids():
    return {int(player["id"]) for player in nba_players.get_active_players()}


def fetch_and_store_traditional_stats(season="2025-26", only_current_players=True):
    traditional = leaguedashplayerstats.LeagueDashPlayerStats(
        measure_type_detailed_defense="Base",
        per_mode_detailed="PerGame",
        season=season,
    )
    df = traditional.get_data_frames()[0]
    allowed_nba_ids = _active_nba_player_ids() if only_current_players else None
    conn = get_connection()
    cur = conn.cursor()
    try:
        player_map = _player_id_map(conn)
        rows = []
        missing_players = set()

        for _, row in df.iterrows():
            nba_player_id = int(row["PLAYER_ID"])
            if allowed_nba_ids is not None and nba_player_id not in allowed_nba_ids:
                continue
            player_id = player_map.get(nba_player_id)
            if not player_id:
                missing_players.add(nba_player_id)
                continue

            rows.append((
                player_id,
                season,
                _null_if_nan(row.get("GP")),
                _null_if_nan(row.get("GS")),
                _null_if_nan(row.get("MIN")),
                _null_if_nan(row.get("PTS")),
                _null_if_nan(row.get("REB")),
                _null_if_nan(row.get("AST")),
                _null_if_nan(row.get("STL")),
                _null_if_nan(row.get("BLK")),
                _null_if_nan(row.get("TOV")),
                _null_if_nan(row.get("FG_PCT")),
                _null_if_nan(row.get("FG3_PCT")),
                _null_if_nan(row.get("FT_PCT")),
            ))

        query = """
            INSERT INTO traditional_stats (
                player_id, season, gp, gs, min_per_game, pts_per_game, reb_per_game,
                ast_per_game, stl_per_game, blk_per_game, tov_per_game, fg_pct, fg3_pct, ft_pct
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (player_id, season)
            DO UPDATE SET
                gp = EXCLUDED.gp,
                gs = EXCLUDED.gs,
                min_per_game = EXCLUDED.min_per_game,
                pts_per_game = EXCLUDED.pts_per_game,
                reb_per_game = EXCLUDED.reb_per_game,
                ast_per_game = EXCLUDED.ast_per_game,
                stl_per_game = EXCLUDED.stl_per_game,
                blk_per_game = EXCLUDED.blk_per_game,
                tov_per_game = EXCLUDED.tov_per_game,
                fg_pct = EXCLUDED.fg_pct,
                fg3_pct = EXCLUDED.fg3_pct,
                ft_pct = EXCLUDED.ft_pct;
        """
        execute_batch(cur, query, rows, page_size=250)
        conn.commit()

        print(f"Completed traditional stats sync for {season}. Rows: {len(rows)}.")
        if missing_players:
            print(
                f"Warning ({season}): skipped {len(missing_players)} players not in players table."
            )
    except Exception as e:
        conn.rollback()
        print(f"Error inserting traditional stats for {season}: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    fetch_and_store_traditional_stats()
