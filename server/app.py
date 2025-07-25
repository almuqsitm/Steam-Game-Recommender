import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env


def get_steam_id64(vanity_name: str, api_key: str) -> str:
    url = f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/"
    params = {"key": api_key, "vanityurl": vanity_name}
    response = requests.get(url, params=params).json()

    if response["response"]["success"] == 1:
        return response["response"]["steamid"]
    else:
        raise ValueError("Invalid Steam vanity name or user is private.")


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
    vanity = input("Enter your Steam username (vanity name): ").strip()

    try:
        steamid = get_steam_id64(vanity, api_key)
        games = get_owned_games(steamid, api_key)

        if not games:
            print("⚠️ No games found or the profile is private.")
            return

        print(f"\n🎮 {vanity}'s Steam Games:")
        for game in sorted(games, key=lambda g: -g["playtime_hours"])[:10]:
            print(f" - {game['name']} ({game['playtime_hours']} hrs)")
    except Exception as e:
        print(f"⚠️ Error: {e}")


if __name__ == "__main__":
    main()
