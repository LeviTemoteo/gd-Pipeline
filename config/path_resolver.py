from pathlib import Path
from config.paths import playtimeTrackerPath

def resolve_playtime_path(deathtracker_path: Path) -> Path:
    '''Remove sufix or rebuild the editor id from deathtracker '''

    name = deathtracker_path.stem
    
    if name.endswith("-editor"):
        name = name.removesuffix("-editor")
        return playtimeTrackerPath / f"Editor-{name}.json"

    for sufix in ("-daily", "-gauntlet", "-local",  "-weekly", "-event"):
        if name.endswith(sufix):
            name = name.removesuffix(sufix)
            break
        
    return playtimeTrackerPath / f"{name}.json"
    
