from models.level import Level
from models.deathTracker import DeathTrackerData
from models.playtimeTracker import PlaytimeTrackerData
from datetime import date

class TransformLevel:
    '''Class that merge deathtracker and playtimetracker data in a level class'''

    def merge(self, DT_data: DeathTrackerData, PT_data: PlaytimeTrackerData, watchdog=False) -> Level:
        '''Main function that return a level object'''

        completion_state = self._define_completion_state(DT_data.current_best)
        
        if watchdog:
            completion_date = self._define_completion_date(completion_state)
        else:
            completion_date = None
        
        cBest = self._define_current_best(DT_data.current_best)
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
        )

    def _define_completion_date(self, completion_state: bool) -> date | None:
        '''Get the date if completion state is True'''
        if completion_state:
            return date.today()
        return None

    def _define_completion_state(self, current_best: int) -> bool:
        '''Verify if current best is  100%'''
        return current_best == 100

    def _define_master_level_id(self, linked_list: list) -> str | None:
        '''Search the smallest id in the list, if the list is empty, return None'''

        # Priority:
        # 1. Online level with the smallest id
        # 2. First local level
        # 3. Editor level with the smallest id
        
        if len(linked_list) <= 1:
            return None

        online = []
        local = []
        editor = []
        
        for level_id in linked_list:
            if level_id.endswith("-local"):
                local.append(level_id)

            elif level_id.endswith("-editor"):
                editor.append(level_id)

            else:
                online.append(level_id)

        if online:
            online_List = []
            for level in online:
                if "-gauntlet" in level:
                    online_List.append(int(level.removesuffix("-gauntlet")))
                elif "-daily" in level:
                    online_List.append(int(level.removesuffix("-daily")))
                else:
                    online_List.append(int(level))
            return min(online_List)
        
        if local:
            return local[0]

        editor_ids = [int(level_id.removesuffix("-editor")) for level_id in editor] # Compare the ids

        return f"{min(editor_ids)}-editor"

    def _define_worst_fail(self, new_bests: list, current_best: int) -> int:
        '''Get the max best less than 100% '''

        if current_best < 100:
            worst_fail = current_best

        elif len(new_bests) >= 2:
            worst_fail = new_bests[-2]

        else:
            worst_fail = 0

        return worst_fail

    def _define_current_best(self, current_best: int) -> int:
        if current_best < 0:
            return 0
        return current_best



                





                
