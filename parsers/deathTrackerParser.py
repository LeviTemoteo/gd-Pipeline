from json import load
from pathlib import Path
from models.deathTracker import DeathTrackerData


class DeathParser:

    def _load_json(self, path: Path) -> dict:
        with open(path, "r", encoding="UTF-8") as file:
            return load(file)

    def parse(self, levelDir: Path) -> DeathTrackerData:
        metadata_path = levelDir / "metadata"
        general_path = levelDir / "general.dt"

        metadata_file = self._load_json(metadata_path)
        general_file = self._load_json(general_path)
        canonical_id = levelDir.name

        return DeathTrackerData(
            canonical_id=canonical_id,
            level_id=self._get_level_id(canonical_id),
            linked_levels=metadata_file.get("LinkedLevels", []),
            level_name=metadata_file.get("levelName", ""),
            difficulty=metadata_file.get("difficulty", 0),
            attempts=metadata_file.get("attempts", 0),
            tracked_attempts=self._get_tracked_attempts(general_file),
            new_bests=general_file.get("newBests", []),
            current_best=general_file.get("currentBest", 0),
        )

    def _get_level_id(self, canonical_id: str) -> str:
        
        """Get the level id using the canonical id and removing unecessary strings"""
        remove = ("-daily", "-gauntlet", "-event", "-weekly")
        level_id = canonical_id

        for item in remove:
            level_id = level_id.removesuffix(item)

        return level_id

    def _get_tracked_attempts(self, generalData: dict) -> int:

        """Sum all tracked runs and deaths receiving general file"""
        deathsDict = generalData.get("deaths", {})
        runsDict = generalData.get("runs", {})

        totalDeaths = sum(deathsDict.values())
        totalRuns = sum(runsDict.values())

        return totalDeaths + totalRuns