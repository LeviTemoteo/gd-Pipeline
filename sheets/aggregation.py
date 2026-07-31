from models.aggregator import AggregatedLevel
from datetime import date
from repository.levelRepository import LevelRepository

class LevelAggregator:

    def agregate_all(self):
        data: list[AggregatedLevel] = []

        with LevelRepository() as database:
            unlinked_levels = database.get_all_unlinked_level_sheets()
            for row in unlinked_levels:
                level_data = AggregatedLevel(
                    level_id=self.resolve_level_id(row["canonical_id"]),
                    level_name=row["level_name"],
                    level_type=self.resolve_type(row["canonical_id"]),
                    difficulty=row["difficulty"],
                    completed=bool(row["completed"]),
                    completion_date=row["completion_date"],
                    attempts=row["attempts"],
                    tracked_attempts=row["tracked_attempts"],
                    playtime=row["playtime"],
                    current_best=row["current_best"],
                    worst_fail=row["worst_fail"])
                data.append(level_data)

            linked_levels = database.get_all_linked_level_aggregates_sheets()
            for row in linked_levels:
                master_id = str(row["master_level_id"])
                all_ids = row["all_canonical_ids"]
                main_playtime = row["main_playtime"]
                total_playtime = row["total_playtime"]

                level_obj = AggregatedLevel(
                    level_id=master_id,
                    level_name=row["level_name"],
                    level_type=self.resolve_type(all_ids),
                    difficulty=row["difficulty"],
                    completed=bool(row["completed"]),
                    completion_date=row["first_completion_date"],
                    attempts=row["total_attempts"],
                    tracked_attempts=row["total_tracked_attempts"],
                    playtime=self.define_playtime(main_playtime, total_playtime, all_ids),
                    current_best=row["current_best"],
                    worst_fail=row["worst_fail"]
                )
                data.append(level_obj)
        return data

    def define_playtime(self, main_playtime: int, total_playtime: int, all_ids: str) -> int:
        with_copy = any(tag in all_ids for tag in ["-daily", "-gauntlet"]) 

        if with_copy:
            return total_playtime - main_playtime
        return total_playtime

    def resolve_type(self, all_canonical_ids: str) -> str:

        all_ids = tuple(all_canonical_ids.split(","))
        priorities = [
            ("Local", lambda canonical_id: "-local" in canonical_id),
            ("Daily", lambda canonical_id: "-daily" in canonical_id),
            ("Gauntlet", lambda canonical_id: "-gauntlet" in canonical_id),
            ("Online", lambda canonical_id: canonical_id.isdigit() or "-" not in canonical_id),
            ("Editor", lambda canonical_id: "-editor" in canonical_id)]
        found_types = []

        for type, func in priorities:
            if any(func(canonical_id) for canonical_id in all_ids):
                    found_types.append(type)

        if not found_types:
            return "Online"

        return "/".join(found_types)

    def resolve_level_id(self, canonical_id: str) -> str:

        sufixes = ["-daily", "-gauntlet"]
        for sufix in sufixes:
            if sufix in canonical_id:
                return canonical_id.removesuffix(sufix)
        return canonical_id
        
        

    
                