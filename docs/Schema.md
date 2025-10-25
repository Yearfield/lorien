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
    medical_dictionary {
      INTEGER id PK
      TEXT    term UNIQUE
      TEXT    definition
      TEXT    synonyms
      INTEGER is_red_flag
      INTEGER avg_children_count
      INTEGER conflicts_count
      TEXT    created_at
      TEXT    updated_at
    }
    shortbow_symptoms {
      INTEGER id PK
      TEXT    symptom_name UNIQUE
      TEXT    created_at
      TEXT    updated_at
    }
    shortbow_symptom_links {
      INTEGER id PK
      INTEGER symptom_from_id FK
      INTEGER symptom_to_id FK
      REAL    probability
      TEXT    created_at
      TEXT    updated_at
      UNIQUE (symptom_from_id, symptom_to_id)
    }
    shortbow_calculations {
      INTEGER id PK
      TEXT    calculation_date
      TEXT    initial_symptom
      TEXT    selected_symptoms
      BOOLEAN saved
      TEXT    created_at
    }
    edge_meta {
      INTEGER parent_id FK
      INTEGER child_id FK
      INTEGER red_flag
      TEXT    created_at
      TEXT    updated_at
      PK (parent_id, child_id)
    }

    nodes ||--o{ nodes : "parent"
    nodes ||--o| triage : "leaf-only"
    nodes ||--o{ node_red_flags : assigns
    red_flags ||--o{ node_red_flags : catalog
    nodes ||--o{ edge_meta : "parent_edge"
    nodes ||--o{ edge_meta : "child_edge"
    medical_dictionary ||--o{ nodes : "syncs_to"
    shortbow_symptoms ||--o{ shortbow_symptom_links : "from_symptom"
    shortbow_symptoms ||--o{ shortbow_symptom_links : "to_symptom"
```

## Canonical columns (CSV)

`Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions`

## Views

- `v_missing_slots(parent_id, missing_slots)` — which slots (1..5) are missing
- `v_next_incomplete_parent(parent_id, missing_slots)` — ordered by depth, parent_id
- `v_paths_complete` — materialized full root→leaf rows for export
- `v_dictionary_with_tree_info` — dictionary terms with tree node relationships and depth labels

## Dictionary Synchronization Triggers

- `tr_sync_dictionary_on_node_change` — updates dictionary when node labels change
- `tr_sync_dictionary_on_node_insert` — adds new terms to dictionary when nodes are inserted
- `tr_sync_dictionary_on_node_delete` — updates dictionary when nodes are deleted
- `tr_sync_nodes_on_dictionary_change` — updates node labels when dictionary terms change
- `tr_sync_red_flags_on_dictionary_change` — handles red flag synchronization
- `tr_medical_dictionary_touch_on_update` — updates timestamp on dictionary changes
