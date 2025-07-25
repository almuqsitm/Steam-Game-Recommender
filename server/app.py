import requests
import os
import re
from dotenv import load_dotenv

load_dotenv()


def extract_steam_identifier(input_str: str) -> str:
    """Extract SteamID64 or vanity name from input"""
    # If it's a full Steam URL
    match = re.match(r"https?://steamcommunity\.com/(id|profiles)/([^/]+)/?", input_str)
    if match:
        return match.group(2)
    return input_str  # Already a name or ID


def get_steam_id64(vanity_name: str, api_key: str) -> str:
    """Convert vanity name to SteamID64, or return ID if already valid"""
    if vanity_name.isdigit() and len(vanity_name) >= 17:
        return vanity_name  # Already a SteamID64
    url = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/"
    params = {"key": api_key, "vanityurl": vanity_name}
    response = requests.get(url, params=params).json()

    if response["response"]["success"] == 1:
        return response["response"]["steamid"]
    else:
        raise ValueError("Invalid Steam vanity name or user is private.")


def get_username(steamid64: str, api_key: str) -> str:
    """Fetch the user's Steam display name"""
    url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    params = {"key": api_key, "steamids": steamid64}
    response = requests.get(url, params=params).json()
    players = response.get("response", {}).get("players", [])
    return players[0]["personaname"] if players else "Unknown"


def get_owned_games(steamid64: str, api_key: str):
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {
        "key": api_key,
        "steamid": steamid64,
        "include_appinfo": 1,
        "format": "json",
    }

    response = requests.get(url, params=params).json()
    games = response.get("response", {}).get("games", [])

    return [
        {
            "appid": game["appid"],
            "name": game["name"],
            "playtime_hours": round(game["playtime_forever"] / 60, 1),
        }
        for game in games
    ]


def main():
    api_key = os.getenv("STEAM_API_KEY") or input("Enter your Steam API key: ")
    raw_input_str = input(
        "Enter your Steam profile link, vanity name, or SteamID64: "
    ).strip()

    try:
        identifier = extract_steam_identifier(raw_input_str)
        steamid = get_steam_id64(identifier, api_key)
        username = get_username(steamid, api_key)
        games = get_owned_games(steamid, api_key)

        if not games:
            print("⚠️ No games found or the profile is private.")
            return

        print(f"\n🎮 {username}'s Steam Games:")
        for game in sorted(games, key=lambda g: -g["playtime_hours"]):
            print(f" - {game['name']} ({game['playtime_hours']} hrs)")
    except Exception as e:
        print(f"⚠️ Error: {e}")


if __name__ == "__main__":
    main()
