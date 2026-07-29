from models.level import Level
from config.paths import dataBasePath
from dataclasses import asdict
from datetime import date
import sqlite3

class LevelRepository:
    def __init__(self):
        self.database_path = dataBasePath
        self.database = None

    def __enter__(self):
        self.database = sqlite3.connect(self.database_path, detect_types=sqlite3.PARSE_DECLTYPES) # detects the date type
        self.database_cursor = self.database.cursor()
        return self
    
    def __exit__(self, exc_type, exc, tb):
        if self.database: # Avoid some errors
            self.database_cursor.close()
            self.database.close()
        
    def insert(self, level: Level) -> None:
        '''Insert a level in DB'''

        sql = ''' 
        insert into levels (canonical_id,
        level_id,
        master_level_id,
        level_name,
        difficulty,
        attempts,
        tracked_attempts,
        current_best,
        worst_fail,
        playtime,
        completed,
        completion_date,
        attempts_synced)
        values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        
        items = list(asdict(level).values())
  
        self.database_cursor.execute(sql, items) 
        self.database.commit()
       

    def update(self, level: Level) -> None:
        '''Update the level in DB'''
        sql = ''' 
        update levels
        set 
            level_id = ?,
            master_level_id = ?,
            level_name = ?,
            difficulty = ?,
            attempts = ?,
            tracked_attempts = ?,
            current_best = ?,
            worst_fail = ?,
            playtime = ?,
            completed = ?,
            completion_date = ?,
            attempts_synced = ?
        where canonical_id = ?
        '''

        params = (
            level.level_id,
            level.master_level_id,
            level.level_name,
            level.difficulty,
            level.attempts,
            level.tracked_attempts,
            level.current_best,
            level.worst_fail,
            level.playtime,
            level.completed,
            level.completion_date,
            level.attempts_synced,
            level.canonical_id
        )
        
        self.database_cursor.execute(sql, params)
        self.database.commit()
        

    def save(self, level: Level) -> None:
        '''Save a Level in DB, choosing among update, insert, update only master id and update attempts'''

        group_completed, group_completion_date = self.get_group_completion(level.master_level_id)

        if group_completed:
            level.completed = True
            level.completion_date = group_completion_date

        existing_level = self.find(level.canonical_id)

        if existing_level:

            # If the level is completed and the level in database is not completed, will get the last update and receive a 0 in attempts_synced
            # This also cover if the level is not completed entire.
            if not existing_level.completed:
                # print(f"Usado o update do if: id {level.level_id} e attempts_synced: {level.attempts_synced}")
                self.update(level)
                if existing_level.attempts_synced is None and level.completed == 1:
                    self.update_attempts_synced(level.canonical_id, 0)
                    level.attempts_synced = 0
                    # print(f"Estado do level após forçar o 0: id {level.level_id} e attempts_synced: {level.attempts_synced}")

            # This elif is for linked levels cases with not completed levels.
            elif existing_level.current_best != 100 and existing_level.completed == 1:

                '''Linked levels that inherited the completion from the original level 
                need to change the attempts_sync when it don't have a current_best == 100,
                this elif cover all of the cases when you disconnect the level.
                '''

                attempts_sync_db = existing_level.attempts_synced
                # if the level is in database and completed = 1, will certainly have attempts_synced = 0
                # with this if else, the level get the update to 1 and don't have a reset in attempts_synced.
                if existing_level.attempts_synced == 0 and level.master_level_id:
                    level.attempts_synced = 1

                else:
                    level.attempts_synced = attempts_sync_db
                    # print(f"trocado o level.attempts_synced pelo o do banco: id {level.level_id} e attempts_synced: {level.attempts_synced}")

                self.update(level)

                # if the level is not linked (don't have a master id) and have a attempts_synced != NULL, will reset.
                if existing_level.attempts_synced in (0, 1) and not existing_level.master_level_id:
                    # print(f"passou o if do elif: id {level.level_id} e attempts_synced: {level.attempts_synced}")
                    self.update_attempts_synced(level.canonical_id, None)
                    level.attempts_synced = None
                    # print(f"Estado do level após forçar o None: id {level.level_id} e attempts_synced: {level.attempts_synced}")
            # if the level is completed and not linked, this else cover.        
            else:
                # print(f"Usado o else (sem update): id {level.level_id} e attempts_synced: {level.attempts_synced}")
                self.update_master_level_id(level.master_level_id, level.canonical_id)
                # When the level attempts_synced is different of 1, will receive 1 (if the level is completed will certainly receive att_sync = 0)
                if level.attempts_synced != 1:
                    self.update_attempts_by_canonical_id(level.canonical_id, level.attempts)
                    self.update_attempts_synced(level.canonical_id, 1)
                    level.attempts_synced = 1
                   # print(f"Usado o else (sem update) e estado depois de forçar 1: id {level.level_id} e attempts_synced: {level.attempts_synced}")
        # else to a level when is not in database.            
        else:
            self.insert(level)

        # Synchronization, if the level is completed and have a master level id, will send the completion = 1, completion_date from the level
        # And the attempts_synced = 0 for everyone else with the same master id.
        print("master_level_id: ", level.master_level_id)
        if level.completed and level.master_level_id:
           # print(f"Fase entrou no sync_linked_levels: id {level.level_id} e attempts_synced: {level.attempts_synced}")
            self.sync_linked_levels(level.master_level_id, level.completion_date, level.attempts_synced)
            
            
    def find(self, canonical_id: str) -> Level | None:
        '''Find a level by its canonical id'''

        sql = '''select * from levels
        where canonical_id = ?
        '''
        self.database_cursor.execute(sql, (canonical_id,))
        newLevel = self.database_cursor.fetchone()

        if newLevel is None:
            return None
        return Level(*newLevel)

    def exists(self, canonical_id: str) -> bool:
        '''See if the level exists in DB'''
        return self.find(canonical_id) is not None
       
    def get_all(self) -> list[Level]:
        '''Return a list of all items with level class'''

        sql = '''select * from levels'''
        self.database_cursor.execute(sql)
        data = self.database_cursor.fetchall()

        levels_list = [Level(*row) for row in data] # Unpacking the DB
        return levels_list

    def clear(self) -> None:
        '''Clean the entire table'''
        
        sql = '''delete from levels'''

        self.database_cursor.execute(sql)
        self.database.commit()

    def delete(self, canonical_id: str) -> None:
        '''Delete one level in DB'''

        sql = '''delete from levels
        where canonical_id = ?
        '''
        self.database_cursor.execute(sql, (canonical_id,))
        self.database.commit()

    def find_linked_levels(self, master_level_id: str | None) -> list[Level]:
        '''Return a list of levels with the same master id or None if don't find any'''

        if master_level_id is None:
            return []
        
        sql = '''select * from levels
        where master_level_id = ?'''
        self.database_cursor.execute(sql, (master_level_id,))
        data = self.database_cursor.fetchall()

        linked_list = [Level(*row) for row in data]
        return linked_list

    def update_master_level_id(self, master_level_id: str, canonical_id: str) -> None:
        '''Update only the master level id in DB'''

        sql = '''UPDATE levels
        set master_level_id = ?
        WHERE canonical_id = ?'''
        self.database_cursor.execute(sql, (master_level_id, canonical_id))
        self.database.commit()

    def sync_linked_levels(self, master_level_id: str, completion_date: date, attempts_sync: int | None) -> None:
        '''Syncronize every linked level with completed True, completion date and attempts_sync = 0'''

        if not master_level_id:
            return

        sql = '''update levels
        set completed = 1
        where master_level_id = ? and completed = 0'''

        self.database_cursor.execute(sql, (master_level_id,))

        if not completion_date:
            return

        #print("Passou pelo completion_date")

        sql = '''update levels
        set completion_date = ?
        where master_level_id = ? and completed = 1 '''

        self.database_cursor.execute(sql, (completion_date, master_level_id))

        if attempts_sync is not None:
            # print("Passou pelo attempts_sync")
            sql = '''update levels
            set attempts_synced = 0
            where master_level_id = ? and attempts_synced IS NULL'''

            self.database_cursor.execute(sql, (master_level_id,))

        self.database.commit()

    def get_group_completion(self, master_level_id: str | None) -> tuple[bool, date | None]:
        ''' Get the completion status and completion Date from a master id'''

        if not master_level_id:
            return False, None

        sql = '''select completion_date from levels
        where master_level_id = ? and completed = 1
        order by completion_date asc
        limit 1'''

        self.database_cursor.execute(sql, (master_level_id,))
        data = self.database_cursor.fetchone()

        if data:
            return True, data[0]
        return False, None

    def find_master_level_id(self, canonical_id: str) -> str | None:
        '''Return the master_level_id by canonical_id'''

        sql = '''
        SELECT master_level_id FROM levels 
        WHERE canonical_id = ?
        '''
        self.database_cursor.execute(sql, (canonical_id,))
        row = self.database_cursor.fetchone()
  
        if row:
            return row[0]
        return None

    def find_attempts_by_canonical_id(self, canonical_id: str) -> int | None:
        '''Return the attempts by canonical_id'''

        sql = '''
        SELECT attempts from levels
        WHERE canonical_id = ?            
        '''
        self.database_cursor.execute(sql, (canonical_id,))
        row = self.database_cursor.fetchone()

        if row:
            return row[0]
        return None

    def update_attempts_by_canonical_id(self, canonical_id: str, attempts: int) -> None:
        '''Update the attempts using the canonical_id. Important for attempts_synced'''
    
        sql = '''
        UPDATE levels
        SET attempts = ?
        WHERE canonical_id = ?            
        '''
        self.database_cursor.execute(sql, (attempts, canonical_id))
        self.database.commit()

    def get_attempts_sync(self, canonical_id: str) -> int | None:
        '''Will return attempts_sync value'''

        sql = '''
        SELECT attempts_synced FROM levels
        WHERE canonical_id = ?
        '''
        self.database_cursor.execute(sql, (canonical_id,))
        row = self.database_cursor.fetchone()

        if row:
            return row[0]
        return None
    
    def update_attempts_synced(self, canonical_id: str, value: int | None) -> None:
        '''Will update attempts_synced by canonical_id and using a value'''

        sql='''
        UPDATE levels
        SET attempts_synced = ? 
        WHERE canonical_id = ?
        '''
        self.database_cursor.execute(sql, (value, canonical_id))
        self.database.commit()
  