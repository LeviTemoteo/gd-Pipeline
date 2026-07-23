from json import load
from pathlib import Path
from models.playtimeTracker import PlaytimeTrackerData


class PlaytimeParser:
    """ Parse Playtime Tracker files into PlaytimeTrackerData objects."""
    def _load_json(self, path: Path) -> dict:
        with open(path, "r", encoding="UTF-8") as file:
            return load(file)

    def parse(self, level_dir: Path) -> PlaytimeTrackerData:
        #level dir is the exact path for the JSON file

        level_File = self._load_json(level_dir)
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
            for init, end in session:
                total += end - init
        return total

