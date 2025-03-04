import os
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo
from datetime import datetime
from database import get_connection  # our previously created connection function
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


# Load environment variables (if needed)
load_dotenv()

def fetch_player_data(full_name):
    # Search for the player by full name
    matching_players = players.find_players_by_full_name(full_name)
    if not matching_players:
        print(f"No player found for: {full_name}")
        return None

    # We take the first match (adjust logic if needed)
    player_info = matching_players[0]
    player_id = player_info['id']
    return player_id

def get_common_player_info(player_id):
    info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
    # Print all data frames returned

    return info.get_data_frames()[0]

def convert_height(height_str):
    """
    Convert a height string in the format "6-9" (feet-inches) into total inches.
    Returns an integer or None if conversion fails.
    """
    try:
        feet, inches = height_str.split('-')
        total_inches = int(feet) * 12 + int(inches)
        return total_inches
    except Exception as e:
        print(f"Error converting height '{height_str}':", e)
        return None
    
def process_player_data(df):
    try:
        full_name = df['DISPLAY_FIRST_LAST'][0]
    except KeyError:
        full_name = None

    try:
        team = df['TEAM_NAME'][0]
    except KeyError:
        team = None

    try:
        position = df['POSITION'][0]
    except KeyError:
        position = None

    try:
        birthdate_raw = df['BIRTHDATE'][0]        
        # If the string contains 'T', assume it's in ISO format and use fromisoformat.
        if 'T' in birthdate_raw:
            birthdate = datetime.fromisoformat(birthdate_raw)
        else:
            birthdate = datetime.strptime(birthdate_raw, '%Y-%m-%d')
    except Exception as e:
        print("Error parsing birthdate:", e)
        birthdate = None

    try:
        raw_height = df['HEIGHT'][0]
        height = convert_height(raw_height)
    except KeyError:
        height = None

    try:
        raw_weight = df['WEIGHT'][0]
        weight = float(raw_weight) if raw_weight else None
    except (KeyError, ValueError):
        weight = None

    return {
        "full_name": full_name,
        "team": team,
        "position": position,
        "birthdate": birthdate,
        "height": height,
        "weight": weight
    }


def insert_player(data):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        query = """
            INSERT INTO players (full_name, team, position, birthdate, height, weight)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (full_name) DO UPDATE 
                SET team = EXCLUDED.team,
                    position = EXCLUDED.position,
                    birthdate = EXCLUDED.birthdate,
                    height = EXCLUDED.height,
                    weight = EXCLUDED.weight
            RETURNING player_id;
        """
        cur.execute(query, (
            data["full_name"],
            data["team"],
            data["position"],
            data["birthdate"],
            data["height"],
            data["weight"]
        ))
        conn.commit()
        result = cur.fetchone()
        player_id = result['player_id']
        print(f"Inserted or updated {data['full_name']} with player_id: {player_id}")
        return player_id
    except Exception as e:
        conn.rollback()
        print("Error inserting/updating player:", e)
    finally:
        cur.close()
        conn.close()


def fetch_and_store_player(full_name):
    # Fetch the player ID from nba_api's static players list
    player_id = fetch_player_data(full_name)
    if not player_id:
        return

    # Fetch detailed common info for that player
    df = get_common_player_info(player_id)
    # Process the DataFrame to extract desired fields
    player_data = process_player_data(df)
    # Insert the processed data into your database
    insert_player(player_data)

if __name__ == "__main__":
    # Test with a sample player (e.g., LeBron James)
    fetch_and_store_player("LeBron James")
