"""
Handles player data loading & searching
"""

import csv
from pathlib import Path
from typing import Dict, List, Tuple

class PlayerDatabase:
    """
    Player Database manager for Tm8s

    Manages loading, storing, searching player info from CSV file
    """
    def __init__(self, csv_file: str = "players_database.csv") -> None:
        """
        Initialize the player database
        :param csv_file: The path to the CSV file containing player data ("players_database.csv")
        """

        self.csv_file = csv_file
        self.players_db: Dict[str, List[tuple[str, int, int]]] = {}
        self.load_database()


    def load_database(self) -> None:
        """
        Load player data from CSV file

        columns: "Player Name", "Club", "Start Year", "End Year"
        Current clubs are currently hard-coded as 2025
        """
        try:
            with open(self.csv_file, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    player_name = row['Player Name']
                    club = row['Club']
                    start_year = int(row['Start Year'])
                    end_year = int(row['End Year'])

                    if player_name not in self.players_db:
                        self.players_db[player_name] = []

                    self.players_db[player_name].append((club, start_year, end_year))

        except Exception as e:
            print(f"Error: {str(e)}")


    def get_all_players(self) -> List[str]:
        """Get list of all player names"""
        return sorted(self.players_db.keys())

    def get_player_data(self, player_name: str) -> List[Tuple[str, int, int]]:
        """
        Get club history for a player

        :arg player_name: The name of the player to retrieve
        """
        return self.players_db.get(player_name, [])

    def search_players(self, query: str) -> List[str]:
        """Search for players by partial name"""
        query = query.lower()
        return [name for name in self.players_db.keys()
                if query in name.lower()]