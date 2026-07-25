from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from time import time, sleep
from pathlib import Path
from orchestrator.orchestrator_main import process_level
from config.path_resolver import resolve_playtime_path
from config.paths import deathTrackerPath

class gdFileHandler(FileSystemEventHandler):

    def __init__(self, debounce: float = 1.0):
        super().__init__()
        self.debounce = debounce
        self._last_modified = {}

    def on_modified(self, event):

        if event.is_directory: # A modified directory don't help us, we need the warning of files.
            return

        file_path = Path(event.src_path)

        if file_path.name != "general.dt": # general is the "main" file
            return

        level_id = file_path.parent.name
        
        now = time()   
        if (now - self._last_modified.get(level_id, 0)) < self.debounce:
            return

        self._last_modified[level_id] = now
        sleep(0.15) # waiting the write in disc

        dir_path = file_path.parent
        process_level(dt_path= dir_path, pt_path = resolve_playtime_path(dir_path), watchdog_state= True) 

def watchdog():
    dog_path = deathTrackerPath

    event_handler = gdFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=str(dog_path), recursive=True)

    observer.start()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()