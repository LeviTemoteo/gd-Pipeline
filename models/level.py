'''Module with level class'''
from dataclasses import dataclass
from datetime import date
    

@dataclass
class Level:
    canonical_id: str
    level_id: str
    master_level_id: str | None = None
    level_name: str = ""
    difficulty: int = 0
    attempts: int = 0
    tracked_attempts: int = 0
    current_best: int = 0
    worst_fail: int = 0
    playtime: int = 0
    completed: bool = False
    completion_date: date | None = None
