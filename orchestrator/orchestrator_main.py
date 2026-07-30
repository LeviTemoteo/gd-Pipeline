from pathlib import Path
from parsers.deathTrackerParser import DeathParser
from parsers.playtimeTrackerParser import PlaytimeParser
from transform.merge import TransformLevel
from repository.levelRepository import LevelRepository


def process_level(dt_path: Path, pt_path: Path, watchdog_state=True) -> None:
    '''Main program, orchestrate the entire process of pipeline'''
    
    dt_data = DeathParser().parse(dt_path)
    # print("Death Parser")
    # dt_data.display()
    if dt_data:
        pt_data = PlaytimeParser().parse(pt_path)
        #print("Playtime Parser")
        #pt_data.display()
        if pt_data:
            level = TransformLevel().merge(DT_data= dt_data, PT_data= pt_data, watchdog=watchdog_state)
            level.show()

            with LevelRepository() as data_base:
                data_base.save(level)