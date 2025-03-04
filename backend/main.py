from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import get_connection
from psycopg2.extras import RealDictCursor

app = FastAPI(title="HoopCast API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for all origins (use carefully)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Pydantic Models
# -----------------------------
#http://127.0.0.1:8000/docs#/
class Player(BaseModel):
    player_id: int
    full_name: str
    team: Optional[str] = None
    position: Optional[str] = None
    birthdate: Optional[str] = None  # Using string for simplicity
    height: Optional[float] = None
    weight: Optional[float] = None

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

class StatPercentiles(BaseModel):
    player_id: int
    off_rating_pct: float
    def_rating_pct: float
    ts_pct_pct: float
    usg_pct_pct: float
    efg_pct_pct: float
    pie_pct: float
    pts_pct: float
    reb_pct: float
    ast_pct: float

# -----------------------------
# Endpoints
# -----------------------------

@app.get("/players", response_model=List[Player])
def get_players():
    """
    Retrieve all players.
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT player_id, full_name, team, position, birthdate, height, weight 
            FROM players;
        """)
        players_list = cur.fetchall()
        return players_list
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
            SELECT player_id, full_name, team, position, TO_CHAR(birthdate, 'YYYY-MM-DD') as birthdate, height, weight 
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
def get_player_by_name(full_name: str):
    """
    Retrieve player details by full name (case-insensitive).
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT player_id, full_name, team, position, TO_CHAR(birthdate, 'YYYY-MM-DD') as birthdate, height, weight 
            FROM players 
            WHERE full_name ILIKE %s;
        """, (full_name,))
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
def get_player_stats(player_id: int, season: str = "2024-25"):
    """
    Retrieve current season stats for a given player.
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT stat_id, player_id, season, off_rating, def_rating, ts_pct, usg_pct, efg_pct, pie, pts, reb, ast
            FROM current_season_stats
            WHERE player_id = %s AND season = %s;
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
def get_player_percentiles(player_id: int, season: str = "2024-25"):
    """
    Retrieve percentile ranks for each stat for a given player for the specified season.
    Uses PostgreSQL window functions to compute percentile ranks across all players.
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Compute percentiles for all players in the given season, then filter for the given player.
        query = """
            WITH ranked AS (
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
                    (1 - PERCENT_RANK() OVER (ORDER BY ast DESC)) * 100 AS ast_pct
                FROM current_season_stats
                WHERE season = %s
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
def get_player_stats_by_name(full_name: str, season: str = "2024-25"):
    # Step 1: Lookup player's internal ID by name
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT player_id FROM players
            WHERE full_name ILIKE %s;
        """, (full_name,))
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
            SELECT stat_id, player_id, season, off_rating, def_rating, ts_pct, usg_pct, efg_pct, pie, pts, reb, ast
            FROM current_season_stats
            WHERE player_id = %s AND season = %s;
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
def get_player_percentiles_by_name(full_name: str, season: str = "2024-25"):
    # First, retrieve the player's ID from the players table
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT player_id FROM players
            WHERE full_name ILIKE %s;
        """, (full_name,))
        player = cur.fetchone()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        player_id = player['player_id']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

    # Now, reuse the existing logic to get percentiles by player_id
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        query = """
            WITH ranked AS (
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
                    (1 - PERCENT_RANK() OVER (ORDER BY ast DESC)) * 100 AS ast_pct
                FROM current_season_stats
                WHERE season = %s
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
