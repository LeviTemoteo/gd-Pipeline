'''Module with level class'''
from dataclasses import dataclass
from datetime import date
    

@dataclass
class Level:
    canonical_id: str
    level_id: str
    level_name: str
    difficulty: int
    attempts: int
    current_best: int
    worst_fail: int
    playtime: int
    completed: bool = False
    completion_date: date | None = None
