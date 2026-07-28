'''Module with playtime tracker data class'''

from dataclasses import dataclass

@dataclass
class PlaytimeTrackerData:
    level_id: str
    playtime: int

    def display(self):
        print(f"[PT] level_id: {self.level_id} | Time: {self.playtime}")