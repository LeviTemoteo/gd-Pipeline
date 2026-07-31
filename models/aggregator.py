'''Module with aggregator class'''
from dataclasses import dataclass
from datetime import date

@dataclass
class AggregatedLevel:
    level_id: str
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

    def to_list(self) -> list:
        '''return a list for google sheets'''

        formatted_date = str(self.completion_date or "")
        
        return [self.level_id,
                self.level_name,
                self.level_type,
                self.difficulty,
                self.completed,
                formatted_date,
                self.attempts,
                self.tracked_attempts,
                self.playtime,
                self.current_best,
                self.worst_fail]

    def display(self):
        '''Display the entire class'''
        print(f"[Aggregation] name: {self.level_name} | type: {self.level_type} | difficulty: {self.difficulty} | completed: {self.completed} | date: {self.completion_date} | attempts: {self.attempts} | tracked_atts: {self.tracked_attempts} | playtime: {self.playtime} | Best: {self.current_best} | worst_fail: {self.worst_fail} | id: {self.level_id}")
    