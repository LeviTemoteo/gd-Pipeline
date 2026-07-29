from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from time import time, sleep
from pathlib import Path
from orchestrator.orchestrator_main import process_level
from config.path_resolver import resolve_playtime_path
from config.paths import deathTrackerPath
from queue import Queue
from threading import Thread

task_queue = Queue()

def worker_consumer():
    last_processed = {}

    while True:
        dir_path = task_queue.get()
        if dir_path is None:
            break

        path_str = str(dir_path)
        now = time()

        if (now - last_processed.get(path_str, 0)) < 0.8:
            task_queue.task_done()
            continue

        last_processed[path_str] = now
        sleep(0.2)
        # print("Fase aceita: ", dir_path)
        process_level(dt_path=dir_path, pt_path= resolve_playtime_path(dir_path), watchdog_state=True)
        task_queue.task_done()

       


class gdFileHandler(FileSystemEventHandler):
    def __init__(self, debounce: float = 0.3):
        super().__init__()

    def on_modified(self, event):

        if event.is_directory: # A modified directory don't help us, we need the warning of files.
            return

        file_path = Path(event.src_path)

        if file_path.name not in ("general.dt", "metadata"):
            return

        if "backups" in file_path.parts:
            parts = file_path.parts
            backup_index = parts.index("backups")
            dir_path = Path(*parts[:backup_index])
        else:
           dir_path = file_path.parent

        # print("Passou nos filtros: ", dir_path)
        task_queue.put(dir_path)


def watchdog():
    worker = Thread(target=worker_consumer, daemon=True)
    worker.start()

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
    task_queue.put(None)
    worker.join()

def get_level_id(level_id: str) -> str:
        """Get the level id using the canonical id and removing unecessary strings"""
        remove = ("-daily", "-gauntlet", "-event", "-weekly", "-editor", "-local")

        for item in remove:
            level_id = level_id.removesuffix(item)

        return level_id 