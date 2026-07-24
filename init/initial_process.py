from config.path_resolver import resolve_playtime_path
from config.paths import deathTrackerPath
from main.orchestrator import process_level
from bootstrap.initialize_db import initialize_database

def initial_scan():
    for dt_path in deathTrackerPath.iterdir():
        if dt_path.name.startswith("."):
            continue
            
        pt_path = resolve_playtime_path(dt_path)
        process_level(dt_path, pt_path)


initialize_database()
initial_scan()
