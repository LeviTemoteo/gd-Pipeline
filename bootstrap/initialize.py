import sqlite3
from config.paths import dataBasePath

def initialize_database():
    dataBase = sqlite3.connect(dataBasePath)
    dataBaseCursor = dataBase.cursor()
    
    sql = '''CREATE TABLE IF NOT EXISTS myGdDataBase
    (canonical_id TEXT PRIMARY KEY,
    level_id TEXT NOT NULL, 
    level_name TEXT NOT NULL,
    difficulty INTEGER NOT NULL,
    attempts INTEGER NOT NULL CHECK (attempts >= 0),
    current_best INTEGER NOT NULL CHECK (current_best BETWEEN 0 AND 100),
    worst_fail INTEGER NOT NULL CHECK (worst_fail BETWEEN 0 AND 99),
    playtime INTEGER NOT NULL CHECK (playtime >= 0),
    completed BOOLEAN NOT NULL DEFAULT FALSE, 
    completion_date DATE)'''

    dataBaseCursor.execute(sql)
    dataBase.commit()
    dataBaseCursor.close()
    dataBase.close()




