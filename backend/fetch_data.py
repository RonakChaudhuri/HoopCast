from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo
from datetime import datetime
from database import get_connection  # our previously created connection function
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


# Load environment variables (if needed)
load_dotenv()

def fetch_player_data(full_name=None, nba_player_id=None):
    if nba_player_id:
        return int(nba_player_id)

    # Search for the player by full name
    if not full_name:
        return None
    matching_players = players.find_players_by_full_name(full_name)
    if not matching_players:
        return None

    # We take the first match (adjust logic if needed)
    player_info = matching_players[0]
    player_id = player_info['id']
    return player_id

def get_common_player_info(player_id):
    info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
    return info.get_data_frames()[0]

def convert_height(height_str):
    """
    Convert a height string in the format "6-9" (feet-inches) into total inches.
    Returns an integer or None if conversion fails.
    """
    if not height_str:
        return None
    try:
        feet, inches = height_str.split('-')
        total_inches = int(feet) * 12 + int(inches)
        return total_inches
    except Exception:
        return None

def _safe_value(df, column_name):
    try:
        value = df[column_name][0]
        if value == "":
            return None
        return value
    except KeyError:
        return None


def _safe_int(value):
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_float(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_birthdate(raw_value):
    if not raw_value:
        return None

    if isinstance(raw_value, datetime):
        return raw_value.date()

    raw_str = str(raw_value).strip()
    if not raw_str:
        return None

    if "T" in raw_str:
        try:
            return datetime.fromisoformat(raw_str.replace("Z", "+00:00")).date()
        except ValueError:
            pass

    for fmt in ("%Y-%m-%d", "%b %d, %Y", "%B %d, %Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw_str.title(), fmt).date()
        except ValueError:
            continue

    return None


def process_player_data(df, nba_player_id, static_info=None, is_active=True, from_year=None, to_year=None):
    full_name = _safe_value(df, "DISPLAY_FIRST_LAST") or (static_info or {}).get("full_name")
    first_name = _safe_value(df, "FIRST_NAME") or (static_info or {}).get("first_name")
    last_name = _safe_value(df, "LAST_NAME") or (static_info or {}).get("last_name")
    team = _safe_value(df, "TEAM_NAME")
    team_abbreviation = _safe_value(df, "TEAM_ABBREVIATION")
    position = _safe_value(df, "POSITION")
    birthdate = _parse_birthdate(_safe_value(df, "BIRTHDATE"))
    height_in = convert_height(_safe_value(df, "HEIGHT"))
    weight_lbs = _safe_float(_safe_value(df, "WEIGHT"))
    country = _safe_value(df, "COUNTRY")
    draft_year = _safe_value(df, "DRAFT_YEAR")
    draft_round = _safe_value(df, "DRAFT_ROUND")
    draft_number = _safe_value(df, "DRAFT_NUMBER")

    # Use static players list values when available for career span and active flag.
    from_year_value = _safe_int(from_year if from_year is not None else (static_info or {}).get("from_year"))
    to_year_value = _safe_int(to_year if to_year is not None else (static_info or {}).get("to_year"))
    is_active_value = bool(is_active if is_active is not None else (static_info or {}).get("is_active", False))

    return {
        "nba_player_id": int(nba_player_id),
        "full_name": full_name,
        "first_name": first_name,
        "last_name": last_name,
        "team": team,
        "team_abbreviation": team_abbreviation,
        "position": position,
        "birthdate": birthdate,
        "height_in": height_in,
        "weight_lbs": weight_lbs,
        "country": country,
        "draft_year": draft_year,
        "draft_round": draft_round,
        "draft_number": draft_number,
        "from_year": from_year_value,
        "to_year": to_year_value,
        "is_active": is_active_value,
    }


def insert_player(data):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        query = """
            INSERT INTO players (
                nba_player_id, full_name, first_name, last_name, team, team_abbreviation,
                position, birthdate, height_in, weight_lbs, country, draft_year,
                draft_round, draft_number, from_year, to_year, is_active
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (nba_player_id) DO UPDATE
                SET full_name = EXCLUDED.full_name,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    team = EXCLUDED.team,
                    team_abbreviation = EXCLUDED.team_abbreviation,
                    position = EXCLUDED.position,
                    birthdate = EXCLUDED.birthdate,
                    height_in = EXCLUDED.height_in,
                    weight_lbs = EXCLUDED.weight_lbs,
                    country = EXCLUDED.country,
                    draft_year = EXCLUDED.draft_year,
                    draft_round = EXCLUDED.draft_round,
                    draft_number = EXCLUDED.draft_number,
                    from_year = EXCLUDED.from_year,
                    to_year = EXCLUDED.to_year,
                    is_active = EXCLUDED.is_active
            RETURNING player_id;
        """
        cur.execute(query, (
            data["nba_player_id"],
            data["full_name"],
            data["first_name"],
            data["last_name"],
            data["team"],
            data["team_abbreviation"],
            data["position"],
            data["birthdate"],
            data["height_in"],
            data["weight_lbs"],
            data["country"],
            data["draft_year"],
            data["draft_round"],
            data["draft_number"],
            data["from_year"],
            data["to_year"],
            data["is_active"],
        ))
        conn.commit()
        result = cur.fetchone()
        player_id = result['player_id']
        return player_id
    except Exception as e:
        conn.rollback()
        print(f"Error inserting/updating player nba_player_id={data.get('nba_player_id')}: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def fetch_and_store_player(full_name=None, nba_player_id=None, is_active=True, from_year=None, to_year=None):
    # Resolve NBA player ID from either input param or full name lookup.
    resolved_nba_player_id = fetch_player_data(full_name=full_name, nba_player_id=nba_player_id)
    if not resolved_nba_player_id:
        return False

    static_info = players.find_player_by_id(resolved_nba_player_id)

    # Fetch detailed common info for that player and process desired fields.
    df = get_common_player_info(resolved_nba_player_id)
    player_data = process_player_data(
        df=df,
        nba_player_id=resolved_nba_player_id,
        static_info=static_info,
        is_active=is_active,
        from_year=from_year,
        to_year=to_year,
    )

    # Insert the processed data into the database.
    inserted_id = insert_player(player_data)
    return inserted_id is not None

if __name__ == "__main__":
    # Test with a sample player.
    fetch_and_store_player(full_name="LeBron James")
