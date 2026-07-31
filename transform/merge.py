from models.level import Level
from models.deathTracker import DeathTrackerData
from models.playtimeTracker import PlaytimeTrackerData
from datetime import date
from repository.levelRepository import LevelRepository

class TransformLevel:
    '''Class that merge deathtracker and playtimetracker data in a level class'''

    def merge(self, DT_data: DeathTrackerData, PT_data: PlaytimeTrackerData, watchdog=True) -> Level:
        '''Main function that return a level object'''

        completion_state = self._define_completion_state(DT_data.current_best)
        cBest = self._define_current_best(DT_data.current_best)
        attempts_synced = self._define_attempts_synced(cBest, watchdog)
        
        if watchdog:
            completion_date = self._define_completion_date(cBest, DT_data.canonical_id)
        else:
            completion_date = None
        
        linked_levels = DT_data.linked_levels.copy()
        linked_levels.append(DT_data.level_id)

        return Level(
            canonical_id = DT_data.canonical_id,
            level_id= DT_data.level_id,
            master_level_id= self._define_master_level_id(linked_levels),
            level_name= DT_data.level_name,
            difficulty= DT_data.difficulty,
            attempts= DT_data.attempts,
            tracked_attempts= DT_data.tracked_attempts,
            current_best= cBest,
            worst_fail= self._define_worst_fail(DT_data.new_bests, cBest),
            playtime= PT_data.playtime,
            completed= completion_state,
            completion_date= completion_date, 
            attempts_synced= attempts_synced 
        )
        
        

    def _define_completion_date(self, current_best: int, canonical_id: str) -> date | None:
        '''Get the date if completion state is True'''
        with LevelRepository() as database:
            existing_level = database.find(canonical_id)

        if existing_level and existing_level.completion_date:
            if existing_level.completed == 0:
                return None
            return existing_level.completion_date

        if current_best == 100:
            #print(f"Entrou no if do current best{current_best}")
            return date.today()
        
        return None

    def _define_completion_state(self, current_best: int) -> bool:
        '''Verify if current best is  100%'''
        return current_best == 100

    def _define_master_level_id(self, original_list: list) -> str | None:
        '''Search the smallest id in the list, if the list is empty, return None. Also define the master id if a linkead already have one'''

        # Priority:
        # 1. Choose between First local level and level already has a master id in db
        # 2. Choose between Online level with the smallest id and level already has a master id in db
        # 3. Choose between Editor level with the smallest id and level already has a master id in db

        linked_list = list(original_list)
        
        if len(linked_list) <= 1:
            return None

        with LevelRepository() as database:
            chain_id = database.find_master_level_id(linked_list[0])
            master_level = database.find(chain_id)

            try: # if the main level don't have a master id, will return None, this try prevent the error.
                if master_level.master_level_id: # Check if the main level has conection with the linked group 
                                                # for some reason, sometimes the main level doesn't have a master_level_id, but the other levels have conection with it
                    linked_list.append(master_level.master_level_id)
            except:
                pass
                    


        
        local = []
        online = []
        editor = []
        
        for level_id in linked_list:
            if level_id.endswith("-local"):
                local.append(int(level_id.removesuffix("-local")))

            elif level_id.endswith("-editor"):
                editor.append(int(level_id.removesuffix("-editor")))

            else:
                online.append(level_id)

        
        if local:
            return f"{min(local)}-local"

        if online:
            online_List = []
            for level in online:
                if "-gauntlet" in level:
                    online_List.append(int(level.removesuffix("-gauntlet")))
                elif "-daily" in level:
                    online_List.append(int(level.removesuffix("-daily")))
                else:
                    online_List.append(int(level))
            return str(min(online_List))
        
        return f"{min(editor)}-editor"

    def _define_worst_fail(self, new_bests: list, current_best: int) -> int:
        '''Get the max best less than 100% '''

        if current_best < 100:
            worst_fail = current_best

        elif len(new_bests) >= 2:
            for best in new_bests[::-1]:
                if best < 100:
                    worst_fail = best
                    return worst_fail
            return 0

        else:
            worst_fail = 0

        return worst_fail

    def _define_current_best(self, current_best: int) -> int:
        if current_best < 0:
            return 0
        return current_best


    def _define_attempts_synced(self, current_best, watchdog: bool) -> int | None:
        if not watchdog and current_best == 100:
            return 1
        
        return None

        





                
