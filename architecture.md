### State Diagram

```mermaid
flowchart LR
    InProgress["Level In Progress"] -->|Exit level| Updating["Updating"]
    Updating -->|Not completed| InProgress
    Updating -->|Level completed| Completed["Completed"]
```
