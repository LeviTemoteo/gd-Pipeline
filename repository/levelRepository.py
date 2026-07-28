from models.level import Level
from config.paths import dataBasePath
from dataclasses import asdict
from datetime import date
import sqlite3

class LevelRepository:
    def __init__(self):
        self.dataBasePath = dataBasePath
        self.dataBase = None
        # dataBase == connection with sqlite DB
        # dataBaseCursor == Cursor

    def __enter__(self):
        self.dataBase = sqlite3.connect(self.dataBasePath, detect_types=sqlite3.PARSE_DECLTYPES) # detects the date type
        return self
    
    def __exit__(self, exc_type, exc, tb):
        if self.dataBase: # Avoid some errors
            self.dataBase.close()
        
    def insert(self, level: Level) -> None:
        '''Insert a level in DB'''

        dataBaseCursor = self.dataBase.cursor()
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
        completion_date)
        values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        
        items = list(asdict(level).values())
  
        dataBaseCursor.execute(sql, items)
        self.dataBase.commit()
        dataBaseCursor.close()   
       

    def update(self, level: Level) -> None:
        '''Update the level in DB'''
        dataBaseCursor = self.dataBase.cursor()
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
            completion_date = ?
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
            level.canonical_id
        )
        
        dataBaseCursor.execute(sql, params)
        self.dataBase.commit()
        dataBaseCursor.close()
        

    def save(self, level: Level) -> None:
        '''Save a Level in DB, choosing among update, insert and update only master id'''
        group_completed, group_completion_date = self.get_group_completion(level.master_level_id)

        if group_completed:
            level.completed = True
            level.completion_date = group_completion_date

        existing_level = self.find(level.canonical_id)

        if existing_level:
            if existing_level.completed:
                self.update_master_level_id(level.master_level_id, level.canonical_id)
            else:
                self.update(level)
        else:
            self.insert(level)

        if level.completed and level.master_level_id:
            self.sync_linked_levels(level.master_level_id, level.completion_date)
            
    def find(self, canonical_id: str) -> Level | None:
        '''Find a level by its canonical id'''
        dataBaseCursor = self.dataBase.cursor()

        sql = '''select * from levels
        where canonical_id = ?
        '''
        dataBaseCursor.execute(sql, (canonical_id,))
        newLevel = dataBaseCursor.fetchone()
        dataBaseCursor.close()

        if newLevel is None:
            return None
        return Level(*newLevel)

    def exists(self, canonical_id: str) -> bool:
        '''See if the level exists in DB'''
        return self.find(canonical_id) is not None
       
    def get_all(self) -> list[Level]:
        '''Return a list of all items with level class'''

        dataBaseCursor = self.dataBase.cursor()
        sql = '''select * from levels'''
        dataBaseCursor.execute(sql)
        data = dataBaseCursor.fetchall()

        levels_list = [Level(*row) for row in data] # Unpacking the DB
        dataBaseCursor.close()

        return levels_list

    def clear(self) -> None:
        '''Clean the entire table'''
        dataBaseCursor = self.dataBase.cursor()
        sql = '''delete from levels'''
        dataBaseCursor.execute(sql)
        self.dataBase.commit()
        dataBaseCursor.close()

    def delete(self, canonical_id: str) -> None:
        '''Delete one level in DB'''

        dataBaseCursor = self.dataBase.cursor()
        sql = '''delete from levels
        where canonical_id = ?
        '''
        dataBaseCursor.execute(sql, (canonical_id,))
        self.dataBase.commit()
        dataBaseCursor.close()

    def find_linked_levels(self, master_level_id: str | None) -> list[Level]:
        '''Return a list of levels with the same master id or None if don't find any'''

        if master_level_id is None:
            return []
        
        dataBaseCursor = self.dataBase.cursor()
        sql = '''select * from levels
        where master_level_id = ?'''
        dataBaseCursor.execute(sql, (master_level_id,))
        data = dataBaseCursor.fetchall()
        dataBaseCursor.close()

        linked_list = [Level(*row) for row in data]
        return linked_list

    def update_master_level_id(self, master_level_id: str, canonical_id: str) -> None:
        '''Update only the master level id in DB'''

        dataBaseCursor = self.dataBase.cursor()
        sql = '''UPDATE levels
        set master_level_id = ?
        WHERE canonical_id = ?'''
        dataBaseCursor.execute(sql, (master_level_id, canonical_id))
        self.dataBase.commit()
        dataBaseCursor.close()

    def sync_linked_levels(self, master_level_id: str, completion_date: date) -> None:
        '''Syncronize every linked level with completed True and completion date'''
        if not master_level_id:
            return

        dataBaseCursor = self.dataBase.cursor()
        sql = '''update levels
        set completed = 1
        where master_level_id = ? and completed = 0'''

        dataBaseCursor.execute(sql, (master_level_id,))

        if not completion_date:
            return

        sql = '''update levels
        set completion_date = ?
        where master_level_id = ? and completed = 1 '''

        dataBaseCursor.execute(sql, (completion_date, master_level_id))
        self.dataBase.commit()
        dataBaseCursor.close()

    def get_group_completion(self, master_level_id: str | None) -> tuple[bool, date | None]:
        ''' Get the completion status and completion Date from a master id'''

        if not master_level_id:
            return False, None

        dataBaseCursor = self.dataBase.cursor()

        sql = '''select completion_date from levels
        where master_level_id = ? and completed = 1
        order by completion_date asc
        limit 1'''

        dataBaseCursor.execute(sql, (master_level_id,))
        data = dataBaseCursor.fetchone()
        dataBaseCursor.close()

        if data:
            return True, data[0]
        return False, None

    def find_master_level_id(self, level_id: str) -> str | None:
        dataBaseCursor = self.dataBase.cursor()

        sql = '''
        SELECT master_level_id FROM levels 
        WHERE level_id = ?
        '''
        dataBaseCursor.execute(sql, (level_id,))
        row = dataBaseCursor.fetchone()
        dataBaseCursor.close()
        if row:
            return row[0]
        return None