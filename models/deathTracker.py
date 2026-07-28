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
    new_bests: list[int]
    current_best: int 

    def display(self):
            print(f"[Level] canonical_id: {self.canonical_id} | level_id: {self.level_id} | linked_levels: {self.linked_levels} | level_name: {self.level_name} | difficulty: {self.difficulty} | attempts: {self.attempts} | tracked_attempts: {self.tracked_attempts} | new_bestes: {self.new_bests} | current_best: {self.current_best}")