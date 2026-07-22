# Linked Progression

## Overview

Death Tracker stores every Geometry Dash level independently, even when multiple copies represent the same logical progression.

Examples include:

- Original level
- Local Start Position copy
- Online practice copy

Each level generates its own JSON files, resulting in multiple independent records for what is effectively the same progression.

gd-Pipeline introduces the concept of **Linked Progression**, allowing these independent levels to be aggregated into a single logical progression during synchronization while preserving each original record inside SQLite.

SQLite always stores the raw data from every level individually.

Aggregation only occurs during synchronization.

---

## Motivation

Many Geometry Dash players practice difficult levels using Start Position copies.

Although these copies generate independent Death Tracker and Playtime Tracker files, they still represent practice for the original level.

Without aggregation:

- Playtime would be fragmented.
- Attempts would be fragmented.
- Statistics would not represent the player's real effort.

gd-Pipeline groups these levels together while preserving their original files.

---

## master_level_id

Every linked level receives a common identifier called `master_level_id`, this identifier represents the logical progression shared by all linked levels.

The value is determined using the linked levels configured inside Death Tracker.

The representative level is chosen as the linked online or local level with the smallest Geometry Dash `level_id`, but if the level is not linked to any other level, `master_level_id` is `NULL`.

Example:

| level_id | master_level_id | level_name |
|----------|-----------------|------------|
| 2241592 | 2241592 | Necropolis |
| 91735946 | 2241592 | Necropolis StartPos |
| 6839035 | 2241592 | Necropolis Copy |

---

## Aggregation Rules

Synchronization groups every level sharing the same `master_level_id`.

The exported statistics are computed using the following rules.

| Field | Aggregation |
|--------|-------------|
| attempts | Sum |
| tracked_attempts | Sum |
| playtime | Sum |
| current_best | Maximum |
| worst_fail | Maximum |
| completed | Any completed level |
| completion_date | Earliest completion date |

SQLite itself never performs this aggregation.

---

## Progression Rules

Not every recorded run represents valid progression.

Runs beginning from a Start Position are considered practice runs.

Only runs starting at **0%** are allowed to modify progression statistics.

The following fields are updated only by valid 0% runs:

- current_best
- worst_fail
- completed
- completion_date

Runs starting from Start Positions are ignored for these fields.

---

## Effort Statistics

Although Start Position runs do not affect progression, they still represent real effort.

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
    worst_fail = new_bests[-2]

else:
    worst_fail = 0
```
Rules:

- Before completion, worst_fail is equal to current_best.
- After completion, worst_fail becomes the last personal best before reaching 100%.
- If the player completed the level without any previous personal best, worst_fail is 0, representing a fluke from 0%.

# Limitations

## Know Limitations
The representative level is selected using the smallest Geometry Dash level_id, so this approach assumes that copied levels are created after the original level.
Although Geometry Dash allows exceptional cases where this assumption may not hold, they are considered extremely rare and are intentionally ignored by the project.

## User Requirements
Linked Progression depends on correct Death Tracker configuration.

For reliable synchronization:
- Linked levels should be configured inside Death Tracker.
- Local copies are recommended whenever possible.
- Unrelated levels should never be linked together.

Failure to follow these recommendations may produce incorrect aggregated statistics.

# Design Decision

## Progress vs Effort

gd-Pipeline distinguishes **player progression** from **player effort**.
Although both are derived from the same gameplay sessions, they measure different aspects of the player's experience and therefore follow different aggregation rules.

---

### Progress

Progress represents the player's legitimate advancement through a level.
Only runs that begin at **0%** are considered valid progression because they reflect a complete attempt from the beginning of the level.

The following fields belong to progression:

- current_best
- worst_fail
- completed
- completion_date

Start Position runs never modify these values.

For example:

```
0% → 52%
```

Updates:

- current_best
- worst_fail

---

```
66% → 100%
```

gd-Pipeline will ignore.
Although the player reached the end of the level, the run did not start from 0%, therefore it does not represent a legitimate completion.

---

### Effort

Effort measures the total amount of practice invested by the player.
Unlike progression, every recorded run represents time spent learning the level, regardless of its starting position.

The following fields belong to effort:

- attempts
- tracked_attempts
- playtime

All runs contribute to these statistics.

For example:

```
0% → 27%
```

gd-Pipeline will counts as effort.

```
66% → 100%
```

Also counts as effort.
Both runs required practice and therefore increase the player's total investment.

---

### Why separate them?

Many Geometry Dash players spend alot of attempts practicing difficult sections using Start Position copies, so ignoring these runs would severely underestimate the player's effort.

However, allowing Start Position runs to update progression would produce misleading statistics, such as:

- Completing a level without ever reaching 100% from 0%.
- Inflated personal bests.
- Incorrect worst fail values.

---

# master_level_id

`master_level_id` is a logical identifier created by gd-Pipeline to group multiple Geometry Dash levels that represent the same progression.
Unlike `canonical_id`, which uniquely identifies each tracked file, `master_level_id` identifies an entire linked progression.

The level id is provided by Death Tracker but the decision of wich id use is computed during the transformation stage by gd-Pipeline.

## Purpose

Death Tracker stores every linked level independently.

For example:

| canonical_id | level_id | level_name |
|---------------|----------|------------|
| 2241592 | 2241592 | Necropolis |
| 91735946 | 91735946 | Necropolis StartPos |
| 6839035 | 6839035 | Necropolis Copy |

Although these files represent the same player progression, each one contains only a portion of the statistics.

`master_level_id` allows gd-Pipeline to recognize that these levels belong to the same **logical progression** while still preserving every original record.

---

## Generation

When Death Tracker reports that two or more levels are linked, gd-Pipeline builds a linked group. The representative identifier is chosen using the smallest numeric Geometry Dash `level_id` among every member of the group.
Every level inside the group receives this value as its `master_level_id`.

Example:

| level_id | master_level_id |
|----------|-----------------|
| 2241592 | 2241592 |
| 91735946 | 2241592 |
| 6839035 | 2241592 |

If a level is not linked to any other level, `master_level_id` is `NULL`.

---

## Why the smallest level_id?

Geometry Dash assigns online level IDs **sequentially**.
Since copies are always created after the original level, the original level will almost always have the smallest numeric identifier.

Using the smallest `level_id` provides:

- Stable identifiers.
- Deterministic grouping.
- No additional metadata stored by the user.

Although RobTop can manually modify a level ID in extremely rare situations, these cases are considered outside the scope of the project.

---

## Lifecycle

`master_level_id` is derived during the Transformation stage every time a linked level is processed.

The value is recalculated from the current Death Tracker linked-level configuration and stored in SQLite together with the level record.
Because it is recomputed on every pipeline execution, changes to linked-level relationships are automatically reflected in the database.

During synchronization, all records sharing the same `master_level_id` are aggregated into a single logical progression.
The original SQLite rows are never merged or removed.

### Note

`master_level_id` is not considered a permanent identifier.

It reflects the current linked-level configuration reported by Death Tracker and may change if the user creates or removes linked-level relationships.

---

## Relationship with canonical_id

These identifiers serve different purposes.

| Identifier | Purpose |
|------------|---------|
| canonical_id | Identifies one physical Death Tracker file |
| level_id | Original Geometry Dash identifier |
| master_level_id | Identifies one logical progression |

This separation allows gd-Pipeline to preserve every original source while still exporting consolidated statistics.
By separating Progress from Effort, gd-Pipeline accurately represents both how far the player legitimately progressed and how much work the player invested to achieve that progress.
