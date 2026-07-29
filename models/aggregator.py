'''Module with aggregator class'''
from dataclasses import dataclass
from datetime import date

@dataclass
class AggregatedLevel:
    level_name: str
    level_type: str
    difficulty: int
    completed: bool
    completion_date: date | None
    attempts: int
    tracked_attempts: int
    playtime: int
    current_best: int
    worst_fail: int
    level_id: str

    def display(self):
        '''Display the entire class'''
        print(f"[Aggregation] name: {self.level_name} | type: {self.level_type} | difficulty: {self.difficulty} | completed: {self.completed} | date: {self.completion_date} | attempts: {self.attempts} | tracked_atts: {self.tracked_attempts} | playtime: {self.playtime} | Best: {self.current_best} | worst_fail: {self.worst_fail} | id: {self.level_id}")
    