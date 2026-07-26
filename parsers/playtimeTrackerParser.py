from json import load, JSONDecodeError
from pathlib import Path
from models.playtimeTracker import PlaytimeTrackerData
from time import sleep

class PlaytimeParser:
    """ Parse Playtime Tracker files into PlaytimeTrackerData objects."""
    def _load_json(self, path: Path) -> dict:
            for _ in range(5):
                try:
                    try:
                        with open(path, "r", encoding="UTF-8") as file:
                            return load(file)
                    except (JSONDecodeError, FileNotFoundError):
                        return {}
                except PermissionError: 
                    sleep(0.2)

    def parse(self, level_dir: Path) -> PlaytimeTrackerData | bool:
        #level dir is the exact path for the JSON file
        if not level_dir.exists():
            return PlaytimeTrackerData(level_id="", playtime=0) # level_id is intentionally ignored, merge.py use the id from death tracker

        level_File = self._load_json(level_dir)

        if not level_File:
            return PlaytimeTrackerData(level_id="", playtime=0)
        
        Id_level = level_dir.stem

        return PlaytimeTrackerData(
            level_id=Id_level,
            playtime=self._get_total_playtime(level_File),
        )
    
    def _get_total_playtime(self, level_file: dict) -> int:
        # Calculates the sum of every session

        sessions = level_file.get("sessions", [])
        total = 0
        for session in sessions:
            for interval in session:
                try:
                    init, end = interval
                    total += end - init
                except (ValueError, TypeError):
                    continue
        return total

