from models.classModule import Level
from config.paths import dataBasePath
from dataclasses import asdict
import sqlite3

class LevelRepository:
    def __init__(self):
        self.dataBasePath = dataBasePath
        self.dataBase = None

    def __enter__(self):
        self.dataBase = sqlite3.connect(self.dataBasePath) 
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
        level_name,
        difficulty,
        attempts,
        tracked_attempts,
        current_best,
        worst_fail,
        playtime,
        completed,
        completion_date)
        values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        
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
        values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''

        params = (
            level.level_id,
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
        dataBaseCursor = self.dataBase.cursor()
        dataBaseCursor.close()

    def find(self, level: Level) -> Level | None:
        '''Find a level by its canonical id.'''
        dataBaseCursor = self.dataBase.cursor()

        sql = '''select * from levels,
        where canonical_id = ?
        values = (?)
        '''
        dataBaseCursor.execute(sql, list(level.canonical_id))
        newLevel = dataBaseCursor.fetchone()
        dataBaseCursor.close()
        return newLevel

        

    def exits(self, level: Level) -> bool:
        dataBaseCursor = self.dataBase.cursor()
        dataBaseCursor.close()

    def get_all(self) -> list[Level]:
        '''Return a list of all items with level class'''

        dataBaseCursor = self.dataBase.cursor()
        sql = '''select * from levels'''
        dataBaseCursor.execute(sql)
        data = dataBaseCursor.fetchall()
        
        levels_list = []

        for row in data:
            levels_list.append(*row) # Unpacking the DB
        dataBaseCursor.close()

        return levels_list

    def clear(self) -> None:
        dataBaseCursor = self.dataBase.cursor()
        dataBaseCursor.close()