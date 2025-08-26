# Data Model & Views

```mermaid
erDiagram
    nodes {
      INTEGER id PK
      INTEGER parent_id FK
      INTEGER depth
      INTEGER slot
      TEXT    label
      INTEGER is_leaf
      TEXT    created_at
      TEXT    updated_at
    }
    triage {
      INTEGER node_id PK FK
      TEXT    diagnostic_triage
      TEXT    actions
      TEXT    created_at
      TEXT    updated_at
    }
    red_flags {
      INTEGER id PK
      TEXT    name UNIQUE
      TEXT    description
      TEXT    severity
      TEXT    created_at
    }
    node_red_flags {
      INTEGER node_id FK
      INTEGER red_flag_id FK
      TEXT    created_at
      PK (node_id, red_flag_id)
    }

    nodes ||--o{ nodes : "parent"
    nodes ||--o| triage : "leaf-only"
    nodes ||--o{ node_red_flags : assigns
    red_flags ||--o{ node_red_flags : catalog
```

## Canonical columns (CSV):
`Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions`

## Views:

- `v_missing_slots(parent_id, missing_slots)` — which slots (1..5) are missing
- `v_next_incomplete_parent(parent_id, missing_slots)` — ordered by depth, parent_id
- `v_paths_complete` — materialized full root→leaf rows for export
