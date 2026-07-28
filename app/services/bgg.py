import os
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()

BGG_SEARCH_URL = "https://boardgamegeek.com/xmlapi2/search"

BGG_TOKEN = os.getenv("BGG_TOKEN")


def search_games(title: str):
    params = {
        "query": title,
        "type": "boardgame"
    }
    headers = {
        "Authorization": f"Bearer {BGG_TOKEN}"
    }
    response = requests.get(BGG_SEARCH_URL, params=params, headers=headers)
    response.raise_for_status()
    root = ET.fromstring(response.text)
    games = []
    for child in root.findall("item"):
        bgg_id = int(child.attrib["id"])
        name_element = child.find("name")
        if name_element is not None:
            name = name_element.attrib["value"]
        else:
            name = None
        year_element = child.find("yearpublished")
        if year_element is not None:
            release_year = int(year_element.attrib["value"])
        else:
            release_year = None
        game = {"bgg_id": bgg_id, "name": name, "release_year": release_year}
        games.append(game)
    return games



