from pathlib import Path
import os

dataDir = Path("data")
dataBasePath = dataDir / "gdDataBase.db"

localAppData = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))

deathTrackerPath = (localAppData / "GeometryDash" / "geode" / "mods" / "elohmrow.death_tracker" / "levels" )
playtimeTrackerPath = (localAppData / "GeometryDash" / "geode" / "mods" / "nanew.playtime-tracker" / "data")

