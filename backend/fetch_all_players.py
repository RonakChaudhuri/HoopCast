import time
from nba_api.stats.static import players
from fetch_data import fetch_and_store_player

def fetch_current_players():
    # This function returns only current active players
    return players.get_active_players()

def fetch_all_players():
    # Includes active and inactive players from the NBA static list.
    return players.get_players()

def fetch_all_players_info(include_inactive=False):
    player_list = fetch_all_players() if include_inactive else fetch_current_players()
    total = len(player_list)
    success_count = 0
    error_count = 0

    for player in player_list:
        full_name = player.get("full_name")
        nba_player_id = player.get("id")
        is_active = bool(player.get("is_active", False))
        from_year = player.get("from_year")
        to_year = player.get("to_year")
        try:
            if fetch_and_store_player(
                full_name=full_name,
                nba_player_id=nba_player_id,
                is_active=is_active,
                from_year=from_year,
                to_year=to_year,
            ):
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            error_count += 1
            print(f"Error processing {full_name}: {e}")
        time.sleep(0.2)

    print(f"Completed player sync. Upserted: {success_count}, Errors: {error_count}, Total: {total}")

def fetch_all_current_players():
    # Backward-compatible function name.
    fetch_all_players_info(include_inactive=False)

if __name__ == "__main__":
    fetch_all_players_info(include_inactive=False)
