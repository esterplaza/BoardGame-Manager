import os
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

from app.schemas.schemas import GameCreate

load_dotenv()

BGG_SEARCH_URL = "https://boardgamegeek.com/xmlapi2/search"

BGG_DETAILS_URL = " https://boardgamegeek.com/xmlapi2/thing"

BGG_TOKEN = os.getenv("BGG_TOKEN")


class BGGService:
    """
    Service responsible for communication with Board Game geek API.
    """
    def __init__(self):
        pass

    def search_games(self, title: str):
        """
        Search BoardGameGeek for games matching a title.

        Args:
            title: Game title to search for.

        Returns:
            list[dict]: list of matching games that contains the BGG ID, title and
            release year.
        """
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
            bgg_id = int(child.get("id"))
            name_element = child.find("name")
            name = name_element.get("value") if name_element is not None else None
            year_element = child.find("yearpublished")
            release_year = int(year_element.get("value")) if year_element is not None else None
            game = {"bgg_id": bgg_id, "name": name, "release_year": release_year}
            games.append(game)
        return games

    def get_game_details(self, bgg_id: int):
        """
        Retrieve detailed information for a board game from BGG API.

        Args:
            bgg_id: Board Game Geek game ID.

        Returns:
            dict: Information for release year, minimum number of players, maximum
            number of players, minimum playing time, maximum playing time, minimum
            age, bgg average rating and box cover image url.
        """
        params = {
            "id": bgg_id,
            "stats": 1
        }
        headers = {
            "Authorization": f"Bearer {BGG_TOKEN}"
        }
        response = requests.get(BGG_DETAILS_URL, params=params, headers=headers)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        item = root.find("item")
        if item is None:
            return None
        name_elements = item.findall("name")
        for element in name_elements:
            if element.get("type") == "primary":
                name = element.get("value")
        thumbnail_element = item.find("thumbnail")
        box_image = thumbnail_element.text if thumbnail_element is not None else None
        year_published_element = item.find("yearpublished")
        release_year = year_published_element.get("value") if year_published_element is not None else None
        min_players_element = item.find("minplayers")
        min_players = min_players_element.get("value") if min_players_element is not None else None
        max_players_element = item.find("maxplayers")
        max_players = max_players_element.get("value") if max_players_element is not None else None
        min_playing_time_element = item.find("minplaytime")
        min_playing_time = min_playing_time_element.get("value") if min_playing_time_element is not None else None
        max_playing_time_element = item.find("maxplaytime")
        max_playing_time = max_playing_time_element.get("value") if max_playing_time_element is not None else None
        min_age_element = item.find("minage")
        min_age = min_age_element.get("value") if min_age_element is not None else None
        statistics_element = item.find("statistics")
        ratings_element = statistics_element.find("ratings") if statistics_element is not None else None
        average_element = ratings_element.find("bayesaverage") if ratings_element is not None else None
        average_rating = average_element.get("value") if average_element is not None else None
        bgg_info = {
            "bgg_id": bgg_id,
            "name": name,
            "release_year": release_year,
            "min_players": min_players,
            "max_players": max_players,
            "min_playing_time": min_playing_time,
            "max_playing_time": max_playing_time,
            "min_age": min_age,
            "average_rating": average_rating,
            "box_image": box_image
        }
        game_create = GameCreate.model_validate(bgg_info)
        return game_create

    def get_game_types(self, bgg_id: int):
        """
        Retrieve game type information for a board game from BGG API.

        Args:
            bgg_id: Board Game Geek game ID.

        Returns:
            dict[list]: Information for categories and mechanic of the game.
        """
        params = {
            "id": bgg_id,
            "stats": 1
        }
        headers = {
            "Authorization": f"Bearer {BGG_TOKEN}"
        }
        response = requests.get(BGG_DETAILS_URL, params=params, headers=headers)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        item = root.find("item")
        if item is None:
            return None
        types = {"categories": [], "mechanics": []}
        link_elements = item.findall("link")
        for element in link_elements:
            if element.get("type") == "boardgamecategory":
                category = element.get("value")
                types["categories"].append(category)
            elif element.get("type") == "boardgamemechanic":
                mechanic = element.get("value")
                types["mechanics"].append(mechanic)
        return types

    def get_game_for_import(self, bgg_id: int):
        """
        Retrieve all information needed to import a game.

        Args:
            bgg_id: Board Game Geek id

        Returns:
            Dictionary containing game details and game types
        """

        details = self.get_game_details(bgg_id)
        types = self.get_game_types(bgg_id)
        return {
            "details": details,
            "types": types
        }
