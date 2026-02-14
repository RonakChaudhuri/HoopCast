import time
import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.static import players as nba_players
from database import get_connection
from psycopg2.extras import execute_batch


def _null_if_nan(value):
    return None if pd.isna(value) else value


def _season_label(start_year):
    return f"{start_year}-{str(start_year + 1)[-2:]}"


def _seasons(start_year, end_year):
    return [_season_label(year) for year in range(start_year, end_year + 1)]


def _player_id_map(conn):
    cur = conn.cursor()
    try:
        cur.execute("SELECT nba_player_id, player_id FROM players;")
        return {int(nba_id): int(player_id) for nba_id, player_id in cur.fetchall()}
    finally:
        cur.close()


def _active_nba_player_ids():
    return {int(player["id"]) for player in nba_players.get_active_players()}


def _upsert_advanced_stats(conn, rows):
    if not rows:
        return
    query = """
        INSERT INTO advanced_stats (
            player_id, season, gp, min_per_game, off_rating, def_rating, net_rating,
            ts_pct, usg_pct, efg_pct, pie, pace, ast_pct, reb_pct, oreb_pct, dreb_pct, tm_tov_pct
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (player_id, season)
        DO UPDATE SET
            gp = EXCLUDED.gp,
            min_per_game = EXCLUDED.min_per_game,
            off_rating = EXCLUDED.off_rating,
            def_rating = EXCLUDED.def_rating,
            net_rating = EXCLUDED.net_rating,
            ts_pct = EXCLUDED.ts_pct,
            usg_pct = EXCLUDED.usg_pct,
            efg_pct = EXCLUDED.efg_pct,
            pie = EXCLUDED.pie,
            pace = EXCLUDED.pace,
            ast_pct = EXCLUDED.ast_pct,
            reb_pct = EXCLUDED.reb_pct,
            oreb_pct = EXCLUDED.oreb_pct,
            dreb_pct = EXCLUDED.dreb_pct,
            tm_tov_pct = EXCLUDED.tm_tov_pct;
    """
    cur = conn.cursor()
    try:
        execute_batch(cur, query, rows, page_size=250)
    finally:
        cur.close()


def _upsert_traditional_stats(conn, rows):
    if not rows:
        return
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
    cur = conn.cursor()
    try:
        execute_batch(cur, query, rows, page_size=250)
    finally:
        cur.close()


def fetch_and_store_season_stats(season, only_current_players=True):
    advanced = leaguedashplayerstats.LeagueDashPlayerStats(
        measure_type_detailed_defense="Advanced",
        per_mode_detailed="PerGame",
        season=season,
    )
    traditional = leaguedashplayerstats.LeagueDashPlayerStats(
        measure_type_detailed_defense="Base",
        per_mode_detailed="PerGame",
        season=season,
    )

    df_adv = advanced.get_data_frames()[0]
    df_trad = traditional.get_data_frames()[0]
    allowed_nba_ids = _active_nba_player_ids() if only_current_players else None

    conn = get_connection()
    try:
        player_map = _player_id_map(conn)

        adv_rows = []
        trad_rows = []
        missing_players = set()

        for _, row in df_adv.iterrows():
            nba_player_id = int(row["PLAYER_ID"])
            if allowed_nba_ids is not None and nba_player_id not in allowed_nba_ids:
                continue
            player_id = player_map.get(nba_player_id)
            if not player_id:
                missing_players.add(nba_player_id)
                continue

            adv_rows.append((
                player_id,
                season,
                _null_if_nan(row.get("GP")),
                _null_if_nan(row.get("MIN")),
                _null_if_nan(row.get("OFF_RATING")),
                _null_if_nan(row.get("DEF_RATING")),
                _null_if_nan(row.get("NET_RATING")),
                _null_if_nan(row.get("TS_PCT")),
                _null_if_nan(row.get("USG_PCT")),
                _null_if_nan(row.get("EFG_PCT")),
                _null_if_nan(row.get("PIE")),
                _null_if_nan(row.get("PACE")),
                _null_if_nan(row.get("AST_PCT")),
                _null_if_nan(row.get("REB_PCT")),
                _null_if_nan(row.get("OREB_PCT")),
                _null_if_nan(row.get("DREB_PCT")),
                _null_if_nan(row.get("TM_TOV_PCT")),
            ))

        for _, row in df_trad.iterrows():
            nba_player_id = int(row["PLAYER_ID"])
            if allowed_nba_ids is not None and nba_player_id not in allowed_nba_ids:
                continue
            player_id = player_map.get(nba_player_id)
            if not player_id:
                missing_players.add(nba_player_id)
                continue

            trad_rows.append((
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

        _upsert_advanced_stats(conn, adv_rows)
        _upsert_traditional_stats(conn, trad_rows)
        conn.commit()
        if missing_players:
            print(
                f"Warning ({season}): skipped {len(missing_players)} players not in players table."
            )
        return len(adv_rows), len(trad_rows)
    except Exception as e:
        conn.rollback()
        print(f"Error while processing season {season}: {e}")
        raise
    finally:
        conn.close()


def fetch_all_season_stats(start_year=2024, end_year=2025, delay_seconds=0.4, only_current_players=True):
    seasons = _seasons(start_year, end_year)
    total_adv = 0
    total_trad = 0
    for season in seasons:
        adv_count, trad_count = fetch_and_store_season_stats(season, only_current_players=only_current_players)
        total_adv += adv_count
        total_trad += trad_count
        time.sleep(delay_seconds)
    print(
        f"Completed stats sync for {len(seasons)} seasons. "
        f"Advanced rows: {total_adv}, Traditional rows: {total_trad}."
    )


if __name__ == "__main__":
    fetch_all_season_stats(start_year=2024, end_year=2025, only_current_players=True)
