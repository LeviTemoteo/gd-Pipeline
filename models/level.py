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
    attempts_synced: int | None = None

    def display(self):
        '''Display the entire class'''
        print(f"[Level] canonical_id: {self.canonical_id} | level_id: {self.level_id} | master_level_id: {self.master_level_id} | level_name: {self.level_name} | difficulty: {self.difficulty} | attempts: {self.attempts} | tracked_attempts: {self.tracked_attempts} | current_best: {self.current_best} | worst_fail: {self.worst_fail} | playtime: {self.playtime} | completed: {self.completed} | completion_date: {self.completion_date} | attempts_synced: {self.attempts_synced}")

    def show(self):
        '''Show only necessary items'''
        print(f"[Level] canonical_id: {self.canonical_id} | level_name: {self.level_name} | difficulty: {self.difficulty} | attempts: {self.attempts} | tracked_attempts: {self.tracked_attempts} | current_best: {self.current_best} | worst_fail: {self.worst_fail} | playtime: {self.playtime} ")
