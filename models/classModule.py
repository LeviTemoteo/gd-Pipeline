'''Module with level class'''
from dataclasses import dataclass
    

@dataclass
class level:
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
