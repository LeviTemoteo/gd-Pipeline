from pathlib import Path
from parsers.deathTrackerParser import DeathParser
from parsers.playtimeTrackerParser import PlaytimeParser
from transform.merge import TransformLevel
from repository.levelRepository import LevelRepository


def process_level(dt_path: Path, pt_path: Path) -> None:
    dt_data = DeathParser().parse(dt_path)

    pt_data = PlaytimeParser().parse(pt_path)

    level = TransformLevel().merge(DT_data= dt_data, PT_data= pt_data)
    

    with LevelRepository() as data_base:
        data_base.save(level)