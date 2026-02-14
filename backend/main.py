from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import get_connection
from psycopg2.extras import RealDictCursor

app = FastAPI(title="HoopCast API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Pydantic Models
# -----------------------------
class Player(BaseModel):
    player_id: int
    full_name: str
    team: Optional[str] = None
    position: Optional[str] = None
    birthdate: Optional[str] = None  # Using string for simplicity
    height: Optional[float] = None
    weight: Optional[float] = None

class PlayerSuggestion(BaseModel):
    player_id: int
    full_name: str
    team: Optional[str] = None

class PlayerStats(BaseModel):
    stat_id: int
    player_id: int
    season: str
    off_rating: Optional[float] = None
    def_rating: Optional[float] = None
    ts_pct: Optional[float] = None
    usg_pct: Optional[float] = None
    efg_pct: Optional[float] = None
    pie: Optional[float] = None
    pts: Optional[float] = None
    reb: Optional[float] = None
    ast: Optional[float] = None
    stl: Optional[float] = None
    blk: Optional[float] = None
    off_rating_on_court: Optional[float] = None
    off_rating_off_court: Optional[float] = None
    def_rating_on_court: Optional[float] = None
    def_rating_off_court: Optional[float] = None
    net_rating_on_court: Optional[float] = None
    net_rating_off_court: Optional[float] = None
    off_rating_on_off_diff: Optional[float] = None
    def_rating_on_off_diff: Optional[float] = None
    net_rating_on_off_diff: Optional[float] = None

class StatPercentiles(BaseModel):
    player_id: int
    off_rating_pct: Optional[float] = None
    def_rating_pct: Optional[float] = None
    ts_pct_pct: Optional[float] = None
    usg_pct_pct: Optional[float] = None
    efg_pct_pct: Optional[float] = None
    pie_pct: Optional[float] = None
    pts_pct: Optional[float] = None
    reb_pct: Optional[float] = None
    ast_pct: Optional[float] = None
    stl_pct: Optional[float] = None
    blk_pct: Optional[float] = None
    off_rating_on_court_pct: Optional[float] = None
    off_rating_off_court_pct: Optional[float] = None
    def_rating_on_court_pct: Optional[float] = None
    def_rating_off_court_pct: Optional[float] = None
    net_rating_on_court_pct: Optional[float] = None
    net_rating_off_court_pct: Optional[float] = None
    off_rating_on_off_diff_pct: Optional[float] = None
    def_rating_on_off_diff_pct: Optional[float] = None
    net_rating_on_off_diff_pct: Optional[float] = None
    
class TraditionalStats(BaseModel):
    stat_id: int
    player_id: int
    season: str
    ppg: Optional[float] = None
    apg: Optional[float] = None
    rpg: Optional[float] = None
    spg: Optional[float] = None
    bpg: Optional[float] = None
    fg_pct: Optional[float] = None
    fg3_pct: Optional[float] = None
    ft_pct: Optional[float] = None

# -----------------------------
# Endpoints
# -----------------------------
@app.get("/")
def read_root():
    return {"message": "Welcome to the HoopCast API"}

@app.get("/players", response_model=List[Player])
def get_players():
    """
    Retrieve all players.
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT
                player_id,
                full_name,
                team,
                position,
                birthdate,
                height_in AS height,
                weight_lbs AS weight
            FROM players;
        """)
        players_list = cur.fetchall()
        return players_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/players/search", response_model=List[PlayerSuggestion])
def search_players(q: str, limit: int = 8):
    """
    Search players by name for autocomplete suggestions.
    """
    q = q.strip()
    if not q:
        return []

    limit = max(1, min(limit, 20))
    search_param = f"%{q}%"
    prefix_param = f"{q}%"

    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT
                player_id,
                full_name,
                team
            FROM players
            WHERE unaccent(full_name) ILIKE unaccent(%s)
            ORDER BY
                CASE
                    WHEN lower(unaccent(full_name)) = lower(unaccent(%s)) THEN 0
                    WHEN lower(unaccent(full_name)) LIKE lower(unaccent(%s)) THEN 1
                    ELSE 2
                END,
                length(full_name),
                full_name
            LIMIT %s;
        """, (search_param, q, prefix_param, limit))
        return cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/players/{player_id}", response_model=Player)
def get_player(player_id: int):
    """
    Retrieve details for a specific player by player_id.
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT
                player_id,
                full_name,
                team,
                position,
                TO_CHAR(birthdate, 'YYYY-MM-DD') as birthdate,
                height_in AS height,
                weight_lbs AS weight
            FROM players 
            WHERE player_id = %s;
        """, (player_id,))
        player = cur.fetchone()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        return player
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/players/by-name/{full_name}", response_model=Player)
@app.get("/players/by-name/{full_name}", response_model=Player)
def get_player_by_name(full_name: str):
    """
    Retrieve player details by a partial match on full name (case-insensitive),
    ignoring diacritics. Returns the first matching result.
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        search_param = f"%{full_name}%"
        cur.execute("""
            SELECT
                player_id,
                full_name,
                team,
                position,
                TO_CHAR(birthdate, 'YYYY-MM-DD') as birthdate,
                height_in AS height,
                weight_lbs AS weight
            FROM players 
            WHERE unaccent(full_name) ILIKE unaccent(%s);
        """, (search_param,))
        player = cur.fetchone()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        return player
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/stats/{player_id}", response_model=PlayerStats)
def get_player_stats(player_id: int, season: str = "2025-26"):
    """
    Retrieve current season stats for a given player by player_id.
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT
                a.stat_id,
                a.player_id,
                a.season,
                a.off_rating,
                a.def_rating,
                a.ts_pct,
                a.usg_pct,
                a.efg_pct,
                a.pie,
                a.off_rating_on_court,
                a.off_rating_off_court,
                a.def_rating_on_court,
                a.def_rating_off_court,
                a.net_rating_on_court,
                a.net_rating_off_court,
                a.off_rating_on_off_diff,
                a.def_rating_on_off_diff,
                a.net_rating_on_off_diff,
                CASE WHEN t.min_per_game > 0 THEN (t.pts_per_game * 36.0 / t.min_per_game) END AS pts,
                CASE WHEN t.min_per_game > 0 THEN (t.reb_per_game * 36.0 / t.min_per_game) END AS reb,
                CASE WHEN t.min_per_game > 0 THEN (t.ast_per_game * 36.0 / t.min_per_game) END AS ast,
                CASE WHEN t.min_per_game > 0 THEN (t.stl_per_game * 36.0 / t.min_per_game) END AS stl,
                CASE WHEN t.min_per_game > 0 THEN (t.blk_per_game * 36.0 / t.min_per_game) END AS blk
            FROM advanced_stats a
            LEFT JOIN traditional_stats t
              ON t.player_id = a.player_id
             AND t.season = a.season
            WHERE a.player_id = %s AND a.season = %s;
        """, (player_id, season))
        stats = cur.fetchone()
        if not stats:
            raise HTTPException(status_code=404, detail="Stats not found for the given player and season")
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/stats/percentiles/{player_id}", response_model=StatPercentiles)
def get_player_percentiles(player_id: int, season: str = "2025-26"):
    """
    Retrieve percentile ranks for each stat for a given player for the specified season.
    Uses PostgreSQL window functions to compute percentile ranks across all players.
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        query = """
            WITH base AS (
                SELECT 
                    a.player_id,
                    a.off_rating,
                    a.def_rating,
                    a.ts_pct,
                    a.usg_pct,
                    a.efg_pct,
                    a.pie,
                    a.off_rating_on_court,
                    a.off_rating_off_court,
                    a.def_rating_on_court,
                    a.def_rating_off_court,
                    a.net_rating_on_court,
                    a.net_rating_off_court,
                    a.off_rating_on_off_diff,
                    a.def_rating_on_off_diff,
                    a.net_rating_on_off_diff,
                    CASE WHEN t.min_per_game > 0 THEN (t.pts_per_game * 36.0 / t.min_per_game) END AS pts,
                    CASE WHEN t.min_per_game > 0 THEN (t.reb_per_game * 36.0 / t.min_per_game) END AS reb,
                    CASE WHEN t.min_per_game > 0 THEN (t.ast_per_game * 36.0 / t.min_per_game) END AS ast,
                    CASE WHEN t.min_per_game > 0 THEN (t.stl_per_game * 36.0 / t.min_per_game) END AS stl,
                    CASE WHEN t.min_per_game > 0 THEN (t.blk_per_game * 36.0 / t.min_per_game) END AS blk
                FROM advanced_stats a
                LEFT JOIN traditional_stats t
                  ON t.player_id = a.player_id
                 AND t.season = a.season
                WHERE a.season = %s
            ),
            ranked AS (
                SELECT
                    player_id,
                    (1 - PERCENT_RANK() OVER (ORDER BY off_rating DESC)) * 100 AS off_rating_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY def_rating ASC)) * 100 AS def_rating_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY ts_pct DESC)) * 100 AS ts_pct_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY usg_pct DESC)) * 100 AS usg_pct_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY efg_pct DESC)) * 100 AS efg_pct_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY pie DESC)) * 100 AS pie_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY pts DESC)) * 100 AS pts_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY reb DESC)) * 100 AS reb_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY ast DESC)) * 100 AS ast_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY stl DESC)) * 100 AS stl_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY blk DESC)) * 100 AS blk_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY off_rating_on_court DESC)) * 100 AS off_rating_on_court_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY off_rating_off_court DESC)) * 100 AS off_rating_off_court_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY def_rating_on_court ASC)) * 100 AS def_rating_on_court_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY def_rating_off_court ASC)) * 100 AS def_rating_off_court_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY net_rating_on_court DESC)) * 100 AS net_rating_on_court_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY net_rating_off_court DESC)) * 100 AS net_rating_off_court_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY off_rating_on_off_diff DESC)) * 100 AS off_rating_on_off_diff_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY def_rating_on_off_diff ASC)) * 100 AS def_rating_on_off_diff_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY net_rating_on_off_diff DESC)) * 100 AS net_rating_on_off_diff_pct
                FROM base
            )
            SELECT * FROM ranked
            WHERE player_id = %s;
        """
        cur.execute(query, (season, player_id))
        result = cur.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Percentile stats not found for the given player and season")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/stats/by-name/{full_name}", response_model=PlayerStats)
@app.get("/stats/by-name/{full_name}", response_model=PlayerStats)
def get_player_stats_by_name(full_name: str, season: str = "2025-26"):
    """
    Retrieve player's current season stats by a partial match on full name (ignoring diacritics).
    Returns the stats for the first matching player.
    """
    # Step 1: Lookup player's internal ID by partial match on name
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        search_param = f"%{full_name}%"
        cur.execute("""
            SELECT player_id FROM players
            WHERE unaccent(full_name) ILIKE unaccent(%s);
        """, (search_param,))
        player = cur.fetchone()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        player_id = player['player_id']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

    # Step 2: Retrieve player's stats by internal ID and season
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT
                a.stat_id,
                a.player_id,
                a.season,
                a.off_rating,
                a.def_rating,
                a.ts_pct,
                a.usg_pct,
                a.efg_pct,
                a.pie,
                a.off_rating_on_court,
                a.off_rating_off_court,
                a.def_rating_on_court,
                a.def_rating_off_court,
                a.net_rating_on_court,
                a.net_rating_off_court,
                a.off_rating_on_off_diff,
                a.def_rating_on_off_diff,
                a.net_rating_on_off_diff,
                CASE WHEN t.min_per_game > 0 THEN (t.pts_per_game * 36.0 / t.min_per_game) END AS pts,
                CASE WHEN t.min_per_game > 0 THEN (t.reb_per_game * 36.0 / t.min_per_game) END AS reb,
                CASE WHEN t.min_per_game > 0 THEN (t.ast_per_game * 36.0 / t.min_per_game) END AS ast,
                CASE WHEN t.min_per_game > 0 THEN (t.stl_per_game * 36.0 / t.min_per_game) END AS stl,
                CASE WHEN t.min_per_game > 0 THEN (t.blk_per_game * 36.0 / t.min_per_game) END AS blk
            FROM advanced_stats a
            LEFT JOIN traditional_stats t
              ON t.player_id = a.player_id
             AND t.season = a.season
            WHERE a.player_id = %s AND a.season = %s;
        """, (player_id, season))
        stats = cur.fetchone()
        if not stats:
            raise HTTPException(status_code=404, detail="Stats not found for the given player and season")
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/stats/percentiles/by-name/{full_name}", response_model=StatPercentiles)
@app.get("/stats/percentiles/by-name/{full_name}", response_model=StatPercentiles)
def get_player_percentiles_by_name(full_name: str, season: str = "2025-26"):
    """
    Retrieve player's percentile ranks by a partial match on full name (ignoring diacritics) for the specified season.
    Returns the percentiles for the first matching player.
    """
    # Step 1: Retrieve player's ID using partial match with unaccent
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        search_param = f"%{full_name}%"
        cur.execute("""
            SELECT player_id FROM players
            WHERE unaccent(full_name) ILIKE unaccent(%s);
        """, (search_param,))
        player = cur.fetchone()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        player_id = player['player_id']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

    # Step 2: Retrieve percentile stats for the player
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        query = """
            WITH base AS (
                SELECT 
                    a.player_id,
                    a.off_rating,
                    a.def_rating,
                    a.ts_pct,
                    a.usg_pct,
                    a.efg_pct,
                    a.pie,
                    a.off_rating_on_court,
                    a.off_rating_off_court,
                    a.def_rating_on_court,
                    a.def_rating_off_court,
                    a.net_rating_on_court,
                    a.net_rating_off_court,
                    a.off_rating_on_off_diff,
                    a.def_rating_on_off_diff,
                    a.net_rating_on_off_diff,
                    CASE WHEN t.min_per_game > 0 THEN (t.pts_per_game * 36.0 / t.min_per_game) END AS pts,
                    CASE WHEN t.min_per_game > 0 THEN (t.reb_per_game * 36.0 / t.min_per_game) END AS reb,
                    CASE WHEN t.min_per_game > 0 THEN (t.ast_per_game * 36.0 / t.min_per_game) END AS ast,
                    CASE WHEN t.min_per_game > 0 THEN (t.stl_per_game * 36.0 / t.min_per_game) END AS stl,
                    CASE WHEN t.min_per_game > 0 THEN (t.blk_per_game * 36.0 / t.min_per_game) END AS blk
                FROM advanced_stats a
                LEFT JOIN traditional_stats t
                  ON t.player_id = a.player_id
                 AND t.season = a.season
                WHERE a.season = %s
            ),
            ranked AS (
                SELECT
                    player_id,
                    (1 - PERCENT_RANK() OVER (ORDER BY off_rating DESC)) * 100 AS off_rating_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY def_rating ASC)) * 100 AS def_rating_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY ts_pct DESC)) * 100 AS ts_pct_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY usg_pct DESC)) * 100 AS usg_pct_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY efg_pct DESC)) * 100 AS efg_pct_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY pie DESC)) * 100 AS pie_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY pts DESC)) * 100 AS pts_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY reb DESC)) * 100 AS reb_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY ast DESC)) * 100 AS ast_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY stl DESC)) * 100 AS stl_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY blk DESC)) * 100 AS blk_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY off_rating_on_court DESC)) * 100 AS off_rating_on_court_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY off_rating_off_court DESC)) * 100 AS off_rating_off_court_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY def_rating_on_court ASC)) * 100 AS def_rating_on_court_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY def_rating_off_court ASC)) * 100 AS def_rating_off_court_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY net_rating_on_court DESC)) * 100 AS net_rating_on_court_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY net_rating_off_court DESC)) * 100 AS net_rating_off_court_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY off_rating_on_off_diff DESC)) * 100 AS off_rating_on_off_diff_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY def_rating_on_off_diff ASC)) * 100 AS def_rating_on_off_diff_pct,
                    (1 - PERCENT_RANK() OVER (ORDER BY net_rating_on_off_diff DESC)) * 100 AS net_rating_on_off_diff_pct
                FROM base
            )
            SELECT * FROM ranked WHERE player_id = %s;
        """
        cur.execute(query, (season, player_id))
        result = cur.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Percentile stats not found for the given player and season")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
        
@app.get("/traditional_stats/{player_id}", response_model=TraditionalStats)
def get_traditional_stats(player_id: int, season: str = "2025-26"):
    """
    Retrieve traditional per-game stats for a given player by player_id.
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Notice the AS clauses mapping db columns -> new names
        cur.execute("""
            SELECT
                stat_id,
                player_id,
                season,
                pts_per_game AS ppg,
                ast_per_game AS apg,
                reb_per_game AS rpg,
                stl_per_game AS spg,
                blk_per_game AS bpg,
                fg_pct,
                fg3_pct,
                ft_pct
            FROM traditional_stats
            WHERE player_id = %s AND season = %s;
        """, (player_id, season))
        stats = cur.fetchone()
        if not stats:
            raise HTTPException(status_code=404, detail="Traditional stats not found for the given player and season")
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


@app.get("/traditional_stats/by-name/{full_name}", response_model=TraditionalStats)
def get_traditional_stats_by_name(full_name: str, season: str = "2025-26"):
    """
    Retrieve traditional per-game stats for a player by a partial match on full name (ignoring diacritics).
    Returns the stats for the first matching player.
    """
    # 1) Lookup player's internal ID
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        search_param = f"%{full_name}%"
        cur.execute("""
            SELECT player_id
            FROM players
            WHERE unaccent(full_name) ILIKE unaccent(%s)
            LIMIT 1;
        """, (search_param,))
        player = cur.fetchone()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        player_id = player['player_id']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

    # 2) Retrieve traditional stats by player_id
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT
                stat_id,
                player_id,
                season,
                pts_per_game AS ppg,
                ast_per_game AS apg,
                reb_per_game AS rpg,
                stl_per_game AS spg,
                blk_per_game AS bpg,
                fg_pct,
                fg3_pct,
                ft_pct
            FROM traditional_stats
            WHERE player_id = %s AND season = %s;
        """, (player_id, season))
        stats = cur.fetchone()
        if not stats:
            raise HTTPException(status_code=404, detail="Traditional stats not found for the given player and season")
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

