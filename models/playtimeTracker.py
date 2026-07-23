'''Module with playtime tracker data class'''

from dataclasses import dataclass

@dataclass
class PlaytimeTrackerData:
    level_id: str
    playtime: int