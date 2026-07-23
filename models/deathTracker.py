'''Module with death tracker data class'''
from dataclasses import dataclass

@dataclass
class DeathTrackerData:
    canonical_id: str
    level_id: str
    linked_levels: list[str]
    level_name: str 
    difficulty: int 
    attempts: int 
    tracked_attempts: int 
    current_best: int 
    worst_fail: int 
    