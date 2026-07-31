<img src="assets/ufo_10.png" alt="Logo" width="110" align="left" />

<h3>Linked Progression</h3>

Death Tracker stores every Geometry Dash level independently, even when multiple copies represent the same logical progression.

Examples include:

- Original level
- Local Start Position copy
- Online practice copy

Each level generates its own JSON files, resulting in multiple independent records for what is effectively the same progression.

gd-Pipeline uses the system of **Linked Progression** from death tracker, allowing these independent levels to share a common logical progression while preserving each original record inside SQLite.

SQLite always stores every level independently, but the completion state and attempts_synced is synchronized between linked levels. Statistics are aggregated only during Google Sheets synchronization.

---

## Motivation

Many Geometry Dash players practice difficult levels using level copies, there you can start from a different position (instead starting from 0%, you can choose to start from 80%), allowing to pratice certain parts of the level, we call this **Start Position**.

Although these copies generate independent Death Tracker and Playtime Tracker files, they still represent practice for the original level.

Without Linked Progression:

- Playtime would be fragmented.
- Attempts would be fragmented.
- Progress would become disconnected.
- Statistics would not represent the player's real effort.

gd-Pipeline groups these levels together using `master_level_id` while preserving every original record.

---

## master_level_id

Every linked level receives a common identifier called `master_level_id`, this identifier represents the logical progression shared by every linked level.

The value is determined using the linked levels configured inside Death Tracker and the original level is chosen as the linked online or local level with the smallest Geometry Dash `level_id`.

If the level is not linked to any other level, `master_level_id` is `NULL`.

Example:

| level_id | master_level_id | level_name |
|----------|-----------------|------------|
| 2241592 | 2241592 | Necropolis |
| 91735946 | 2241592 | Necropolis StartPos |
| 6839035 | 2241592 | Necropolis Copy |
| 79922944 | NULL | Dole Damos |

---

## Completion Synchronization

Each linked level remains an independent SQLite record.

After a level is persisted, gd-Pipeline synchronizes the completion state across every record sharing the same `master_level_id`.

Fields that are synchronized:

- completed
- attempts_synced

This guarantees that every linked level consistently represents the completion state of the same logical progression while preserving its own gameplay statistics.

---

## Aggregation Rules

Synchronization with Google Sheets groups every level sharing the same `master_level_id`.

The exported statistics are computed using the following rules.

| Field | Aggregation |
|--------|-------------|
| attempts | Sum |
| tracked_attempts | Sum |
| playtime | Maximum or Sum |
| current_best | Maximum |
| worst_fail | Maximum |
| completed | Already synchronized |
| completion_date | Minimum |

SQLite does not performs this aggregation.

---

## Progression Rules

Not every recorded run represents valid progression, runs from a Start Position are considered "practice" runs, because of that only runs starting at **0%** are allowed to modify progression statistics.

The following fields are updated only by valid 0% runs:

- current_best
- worst_fail
- completed
- completion_date

Runs from Start Positions are ignored for these fields.

---

## Effort Statistics

Although Start Position do not affect progression, they still represent real effort.

Therefore they always contribute to:

- attempts
- tracked_attempts
- playtime

This allows the synchronized statistics to represent the player's total investment while keeping progression statistics accurate.

---

## Worst Fail Algorithm

`worst_fail` is computed by gd-Pipeline rather than being read directly from Death Tracker.

Algorithm:

```python
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
```

Rules:

- Before completion, `worst_fail` is equal to `current_best`.
- After completion, `worst_fail` becomes the last best before reaching 100%.
- If the player completed the level without any previous best, `worst_fail` is `0`, representing a fluke from 0%.

`new_bests` list is only used during transformation and is not stored in SQLite.

---

# Limitations

## Known Limitations

The representative level is selected using the smallest Geometry Dash `level_id`, so this approach assumes that copied levels are created after the original level.

Although Geometry Dash allows exceptional cases where this assumption may not hold, they are considered extremely rare and are intentionally ignored by the project.

## User Requirements

Linked Progression depends on correct Death Tracker configuration.

For reliable synchronization:

- Linked levels should be configured inside Death Tracker.
- Local copies are recommended whenever possible.
- Unrelated levels should never be linked together.
- Link all copies only in original level death tracker menu.

Failure to follow these recommendations **may** produce incorrect aggregated statistics.

---

# Design Decisions

## Progress vs Effort

gd-Pipeline distinguishes **player progression** from **player effort**.

Although both are derived from the same gameplay sessions, they measure different aspects of the player's experience and therefore follow different processing rules.

### Progress

Progress represents the player's legitimate advancement through a level, then only runs that begin at **0%** are considered valid progression because they reflect a complete attempt from the beginning of the level.

The following fields belong to progression:

- current_best
- worst_fail
- completed
- completion_date

Start Position copies never modify these values.

For example:

```
0% -> 52%
```

Updates:

- current_best
- worst_fail

---

```
66% -> 100%
```

gd-Pipeline ignores this completion because the run did not begin from 0%.

---

### Effort

Effort measures the total amount of practice invested by the player.

Unlike progression, every recorded run represents time spent learning the level regardless of its starting position.

The following fields belong to effort:

- attempts
- tracked_attempts
- playtime

For example:

```
0% -> 27%
```

Counts as effort.

```
66% -> 100%
```

Also counts as effort.

---

### Why separate them?

Many Geometry Dash players spend thousands of attempts practicing difficult sections using Start Position copies.

Ignoring these runs would severely underestimate the player's effort.

However, allowing Start Position copies runs to update progression would produce misleading statistics such as:

- Completing a level without reaching 100% from 0%.
- Inflated personal bests.
- Incorrect worst fail values.

---

## Independent SQLite Records

Every linked level remains stored independently.

SQLite reflects the original data generated by Death Tracker and Playtime Tracker.

---

## Group Completion State

Completion belongs to the logical progression rather than an individual level file.

For this reason, completed and attempts_synced are synchronized immediately after persistence across every level sharing the same `master_level_id`.

---

## Aggregation During Synchronization

Gameplay statistics remain independent inside SQLite.

Only during synchronization with Google Sheets are linked levels aggregated into a single logical progression using the aggregation rules defined by gd-Pipeline.
Check docs/architecture to see some examples.
