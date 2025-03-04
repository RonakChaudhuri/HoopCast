import time
from nba_api.stats.static import players
from fetch_data import fetch_and_store_player

def fetch_current_players():
    # This function returns only current active players
    return players.get_active_players()

def fetch_all_current_players():
    all_current_players = fetch_current_players()
    total = len(all_current_players)
    print(f"Total active players found: {total}")

    for i, player in enumerate(all_current_players, start=1):
        full_name = player.get("full_name")
        #print(f"[{i}/{total}] Processing: {full_name}")
        try:
            fetch_and_store_player(full_name)
        except Exception as e:
            print(f"Error processing {full_name}: {e}")
        time.sleep(.5)  # Adjust the delay as needed

if __name__ == "__main__":
    fetch_all_current_players()
