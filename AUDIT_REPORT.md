# Wiring Audit Report

Generated: `2025-09-08T18:58:43`

## Backend routes

| Path | Methods | Name |
| --- | --- | --- |
| / | GET | root |
| /admin/clear | POST | admin_clear |
| /admin/clear-nodes | POST | clear_nodes_endpoint |
| /admin/roots/suspect | GET | suspect_roots |
| /admin/sanitize-labels | POST | sanitize_labels |
| /admin/sync-dictionary-from-tree | POST | sync_dictionary_from_tree |
| /api/v1/ | GET | root |
| /api/v1/admin/clear | POST | admin_clear |
| /api/v1/admin/clear-nodes | POST | clear_nodes_endpoint |
| /api/v1/admin/roots/suspect | GET | suspect_roots |
| /api/v1/admin/sanitize-labels | POST | sanitize_labels |
| /api/v1/admin/sync-dictionary-from-tree | POST | sync_dictionary_from_tree |
| /api/v1/backup | POST | create_backup |
| /api/v1/backup/status | GET | get_backup_status |
| /api/v1/calc/export | GET | export_calculator_csv |
| /api/v1/calc/export.xlsx | GET | export_calculator_xlsx |
| /api/v1/dictionary | GET | list_terms |
| /api/v1/dictionary | POST | create_term |
| /api/v1/dictionary/normalize | GET | normalize_term |
| /api/v1/flags | GET | list_flags |
| /api/v1/flags/assign | POST | assign_flag |
| /api/v1/flags/assign | POST | assign_flag |
| /api/v1/flags/audit | GET | get_audit |
| /api/v1/flags/audit/ | GET | get_audit |
| /api/v1/flags/audit/ | POST | create_audit |
| /api/v1/flags/preview-assign | GET | preview_flag_assignment |
| /api/v1/flags/remove | POST | remove_flag |
| /api/v1/flags/remove | POST | remove_flag |
| /api/v1/flags/search | GET | search_flags |
| /api/v1/health | GET | health_check |
| /api/v1/health/metrics | GET | health_metrics |
| /api/v1/import | POST | import_file |
| /api/v1/import/excel | POST | import_excel |
| /api/v1/import/jobs | GET | get_import_jobs |
| /api/v1/import/jobs/{job_id:int} | GET | get_import_job |
| /api/v1/import/preview | POST | import_preview |
| /api/v1/llm/fill-triage-actions | POST | llm_fill |
| /api/v1/llm/health | GET | llm_health |
| /api/v1/outcomes/triage/{node_id:int} | PUT | update_triage_legacy |
| /api/v1/outcomes/{node_id:int} | PUT | update_outcomes |
| /api/v1/red-flags/audit | GET | get_audit |
| /api/v1/red-flags/bulk-attach | POST | bulk_attach |
| /api/v1/red-flags/bulk-detach | POST | bulk_detach |
| /api/v1/restore | POST | restore_backup |
| /api/v1/tree/children | GET | list_children |
| /api/v1/tree/children/{parent_id} | GET | get_children |
| /api/v1/tree/conflicts | GET | conflicts_root |
| /api/v1/tree/conflicts/conflicts | GET | get_conflicts |
| /api/v1/tree/conflicts/depth-anomalies | GET | get_depth_anomalies |
| /api/v1/tree/conflicts/depth-anomalies | GET | get_depth_anomalies |
| /api/v1/tree/conflicts/duplicate-labels | GET | get_duplicate_labels |
| /api/v1/tree/conflicts/duplicate-labels | GET | get_duplicate_labels |
| /api/v1/tree/conflicts/group | GET | conflicts_group |
| /api/v1/tree/conflicts/group/resolve | POST | conflicts_group_resolve |
| /api/v1/tree/conflicts/orphans | GET | get_orphans |
| /api/v1/tree/conflicts/orphans | GET | get_orphan_nodes |
| /api/v1/tree/conflicts/parent/{parent_id}/merge-duplicates | POST | post_merge_dupes |
| /api/v1/tree/conflicts/parent/{parent_id}/normalize | POST | post_normalize |
| /api/v1/tree/export | GET | export_tree_csv |
| /api/v1/tree/export-json | GET | tree_export |
| /api/v1/tree/export.xlsx | GET | export_tree_xlsx |
| /api/v1/tree/labels | GET | get_labels |
| /api/v1/tree/labels/{label}/aggregate | GET | get_label_aggregate |
| /api/v1/tree/labels/{label}/apply-default | POST | post_apply_default |
| /api/v1/tree/leaves | GET | list_leaves |
| /api/v1/tree/materialize | POST | materialize_tree |
| /api/v1/tree/materialize/runs | GET | get_materialization_history |
| /api/v1/tree/materialize/undo | POST | undo_materialization |
| /api/v1/tree/missing-slots | GET | get_missing_slots |
| /api/v1/tree/missing-slots | GET | get_missing_slots |
| /api/v1/tree/missing-slots-json | GET | tree_missing_slots |
| /api/v1/tree/navigate | GET | get_navigate |
| /api/v1/tree/next-incomplete-parent | GET | get_next_incomplete_parent |
| /api/v1/tree/next-incomplete-parent | GET | get_next_incomplete_parent |
| /api/v1/tree/next-incomplete-parent | GET | get_next_incomplete_parent |
| /api/v1/tree/next-incomplete-parent-json | GET | get_next_incomplete_parent |
| /api/v1/tree/parent/{parent_id:int}/children | GET | read_parent_children |
| /api/v1/tree/parent/{parent_id:int}/children | PUT | update_parent_children |
| /api/v1/tree/parents | GET | get_parents |
| /api/v1/tree/parents/incomplete | GET | list_incomplete_parents |
| /api/v1/tree/path | GET | get_node_path |
| /api/v1/tree/root-options | GET | get_root_options |
| /api/v1/tree/roots | GET | get_roots |
| /api/v1/tree/roots | GET | list_roots |
| /api/v1/tree/roots | POST | create_vital_measurement |
| /api/v1/tree/stats | GET | tree_stats |
| /api/v1/tree/stats | GET | get_tree_stats |
| /api/v1/tree/suggest/labels | GET | suggest_labels |
| /api/v1/tree/vm | POST | create_vm |
| /api/v1/tree/wizard/sheet | POST | stage_sheet_wizard |
| /api/v1/tree/wizard/sheet/commit | POST | commit_sheet_wizard |
| /api/v1/tree/{node_id} | DELETE | delete_parent |
| /api/v1/tree/{parent_id:int} | GET | get_parent_info |
| /api/v1/tree/{parent_id:int}/child | POST | insert_child |
| /api/v1/tree/{parent_id:int}/children | GET | get_children |
| /api/v1/tree/{parent_id:int}/children | GET | get_parent_children |
| /api/v1/tree/{parent_id:int}/children | POST | upsert_children |
| /api/v1/tree/{parent_id:int}/children | POST | bulk_update_children |
| /api/v1/tree/{parent_id:int}/slot/{slot:int} | DELETE | delete_slot |
| /api/v1/tree/{parent_id:int}/slot/{slot:int} | PUT | upsert_slot |
| /api/v1/tree/{parent_id}/slot/{slot} | PUT | put_child_slot |
| /api/v1/triage/search | GET | search_triage |
| /api/v1/triage/{node_id:int} | GET | get_triage |
| /api/v1/triage/{node_id:int} | PUT | update_triage |
| /backup | POST | create_backup |
| /backup/status | GET | get_backup_status |
| /calc/export | GET | export_calculator_csv |
| /calc/export.xlsx | GET | export_calculator_xlsx |
| /dictionary | GET | list_terms |
| /dictionary | POST | create_term |
| /dictionary/normalize | GET | normalize_term |
| /flags | GET | list_flags |
| /flags/assign | POST | assign_flag |
| /flags/assign | POST | assign_flag |
| /flags/audit | GET | get_audit |
| /flags/audit/ | GET | get_audit |
| /flags/audit/ | POST | create_audit |
| /flags/preview-assign | GET | preview_flag_assignment |
| /flags/remove | POST | remove_flag |
| /flags/remove | POST | remove_flag |
| /flags/search | GET | search_flags |
| /health | GET | health_check |
| /health/metrics | GET | health_metrics |
| /import | POST | import_file |
| /import/excel | POST | import_excel |
| /import/jobs | GET | get_import_jobs |
| /import/jobs/{job_id:int} | GET | get_import_job |
| /import/preview | POST | import_preview |
| /llm/fill-triage-actions | POST | llm_fill |
| /llm/health | GET | llm_health |
| /outcomes/triage/{node_id:int} | PUT | update_triage_legacy |
| /outcomes/{node_id:int} | PUT | update_outcomes |
| /red-flags/audit | GET | get_audit |
| /red-flags/bulk-attach | POST | bulk_attach |
| /red-flags/bulk-detach | POST | bulk_detach |
| /restore | POST | restore_backup |
| /tree/children | GET | list_children |
| /tree/children/{parent_id} | GET | get_children |
| /tree/conflicts | GET | conflicts_root |
| /tree/conflicts/conflicts | GET | get_conflicts |
| /tree/conflicts/depth-anomalies | GET | get_depth_anomalies |
| /tree/conflicts/depth-anomalies | GET | get_depth_anomalies |
| /tree/conflicts/duplicate-labels | GET | get_duplicate_labels |
| /tree/conflicts/duplicate-labels | GET | get_duplicate_labels |
| /tree/conflicts/group | GET | conflicts_group |
| /tree/conflicts/group/resolve | POST | conflicts_group_resolve |
| /tree/conflicts/orphans | GET | get_orphans |
| /tree/conflicts/orphans | GET | get_orphan_nodes |
| /tree/conflicts/parent/{parent_id}/merge-duplicates | POST | post_merge_dupes |
| /tree/conflicts/parent/{parent_id}/normalize | POST | post_normalize |
| /tree/export | GET | export_tree_csv |
| /tree/export-json | GET | tree_export |
| /tree/export.xlsx | GET | export_tree_xlsx |
| /tree/labels | GET | get_labels |
| /tree/labels/{label}/aggregate | GET | get_label_aggregate |
| /tree/labels/{label}/apply-default | POST | post_apply_default |
| /tree/leaves | GET | list_leaves |
| /tree/materialize | POST | materialize_tree |
| /tree/materialize/runs | GET | get_materialization_history |
| /tree/materialize/undo | POST | undo_materialization |
| /tree/missing-slots | GET | get_missing_slots |
| /tree/missing-slots | GET | get_missing_slots |
| /tree/missing-slots-json | GET | tree_missing_slots |
| /tree/navigate | GET | get_navigate |
| /tree/next-incomplete-parent | GET | get_next_incomplete_parent |
| /tree/next-incomplete-parent | GET | get_next_incomplete_parent |
| /tree/next-incomplete-parent | GET | get_next_incomplete_parent |
| /tree/next-incomplete-parent-json | GET | get_next_incomplete_parent |
| /tree/parent/{parent_id:int}/children | GET | read_parent_children |
| /tree/parent/{parent_id:int}/children | PUT | update_parent_children |
| /tree/parents | GET | get_parents |
| /tree/parents/incomplete | GET | list_incomplete_parents |
| /tree/path | GET | get_node_path |
| /tree/root-options | GET | get_root_options |
| /tree/roots | GET | get_roots |
| /tree/roots | GET | list_roots |
| /tree/roots | POST | create_vital_measurement |
| /tree/stats | GET | tree_stats |
| /tree/stats | GET | get_tree_stats |
| /tree/suggest/labels | GET | suggest_labels |
| /tree/vm | POST | create_vm |
| /tree/wizard/sheet | POST | stage_sheet_wizard |
| /tree/wizard/sheet/commit | POST | commit_sheet_wizard |
| /tree/{node_id} | DELETE | delete_parent |
| /tree/{parent_id:int} | GET | get_parent_info |
| /tree/{parent_id:int}/child | POST | insert_child |
| /tree/{parent_id:int}/children | GET | get_children |
| /tree/{parent_id:int}/children | GET | get_parent_children |
| /tree/{parent_id:int}/children | POST | upsert_children |
| /tree/{parent_id:int}/children | POST | bulk_update_children |
| /tree/{parent_id:int}/slot/{slot:int} | DELETE | delete_slot |
| /tree/{parent_id:int}/slot/{slot:int} | PUT | upsert_slot |
| /tree/{parent_id}/slot/{slot} | PUT | put_child_slot |
| /triage/search | GET | search_triage |
| /triage/{node_id:int} | GET | get_triage |
| /triage/{node_id:int} | PUT | update_triage |


## Dual-mount compliance

| Base Path | Status | Examples |
| --- | --- | --- |
| / | OK | /, /api/v1/ |
| /admin/clear | OK | /admin/clear, /api/v1/admin/clear |
| /admin/clear-nodes | OK | /admin/clear-nodes, /api/v1/admin/clear-nodes |
| /admin/roots/suspect | OK | /admin/roots/suspect, /api/v1/admin/roots/suspect |
| /admin/sanitize-labels | OK | /admin/sanitize-labels, /api/v1/admin/sanitize-labels |
| /admin/sync-dictionary-from-tree | OK | /admin/sync-dictionary-from-tree, /api/v1/admin/sync-dictionary-from-tree |
| /backup | OK | /api/v1/backup, /backup |
| /backup/status | OK | /api/v1/backup/status, /backup/status |
| /calc/export | OK | /api/v1/calc/export, /calc/export |
| /calc/export.xlsx | OK | /api/v1/calc/export.xlsx, /calc/export.xlsx |
| /dictionary | OK | /api/v1/dictionary, /api/v1/dictionary, /dictionary, /dictionary |
| /dictionary/normalize | OK | /api/v1/dictionary/normalize, /dictionary/normalize |
| /flags | OK | /api/v1/flags, /flags |
| /flags/assign | OK | /api/v1/flags/assign, /api/v1/flags/assign, /flags/assign, /flags/assign |
| /flags/audit | OK | /api/v1/flags/audit, /flags/audit |
| /flags/audit/ | OK | /api/v1/flags/audit/, /api/v1/flags/audit/, /flags/audit/, /flags/audit/ |
| /flags/preview-assign | OK | /api/v1/flags/preview-assign, /flags/preview-assign |
| /flags/remove | OK | /api/v1/flags/remove, /api/v1/flags/remove, /flags/remove, /flags/remove |
| /flags/search | OK | /api/v1/flags/search, /flags/search |
| /health | OK | /api/v1/health, /health |
| /health/metrics | OK | /api/v1/health/metrics, /health/metrics |
| /import | OK | /api/v1/import, /import |
| /import/excel | OK | /api/v1/import/excel, /import/excel |
| /import/jobs | OK | /api/v1/import/jobs, /import/jobs |
| /import/jobs/{job_id:int} | OK | /api/v1/import/jobs/{job_id:int}, /import/jobs/{job_id:int} |
| /import/preview | OK | /api/v1/import/preview, /import/preview |
| /llm/fill-triage-actions | OK | /api/v1/llm/fill-triage-actions, /llm/fill-triage-actions |
| /llm/health | OK | /api/v1/llm/health, /llm/health |
| /outcomes/triage/{node_id:int} | OK | /api/v1/outcomes/triage/{node_id:int}, /outcomes/triage/{node_id:int} |
| /outcomes/{node_id:int} | OK | /api/v1/outcomes/{node_id:int}, /outcomes/{node_id:int} |
| /red-flags/audit | OK | /api/v1/red-flags/audit, /red-flags/audit |
| /red-flags/bulk-attach | OK | /api/v1/red-flags/bulk-attach, /red-flags/bulk-attach |
| /red-flags/bulk-detach | OK | /api/v1/red-flags/bulk-detach, /red-flags/bulk-detach |
| /restore | OK | /api/v1/restore, /restore |
| /tree/children | OK | /api/v1/tree/children, /tree/children |
| /tree/children/{parent_id} | OK | /api/v1/tree/children/{parent_id}, /tree/children/{parent_id} |
| /tree/conflicts | OK | /api/v1/tree/conflicts, /tree/conflicts |
| /tree/conflicts/conflicts | OK | /api/v1/tree/conflicts/conflicts, /tree/conflicts/conflicts |
| /tree/conflicts/depth-anomalies | OK | /api/v1/tree/conflicts/depth-anomalies, /api/v1/tree/conflicts/depth-anomalies, /tree/conflicts/depth-anomalies, /tree/conflicts/depth-anomalies |
| /tree/conflicts/duplicate-labels | OK | /api/v1/tree/conflicts/duplicate-labels, /api/v1/tree/conflicts/duplicate-labels, /tree/conflicts/duplicate-labels, /tree/conflicts/duplicate-labels |
| /tree/conflicts/group | OK | /api/v1/tree/conflicts/group, /tree/conflicts/group |
| /tree/conflicts/group/resolve | OK | /api/v1/tree/conflicts/group/resolve, /tree/conflicts/group/resolve |
| /tree/conflicts/orphans | OK | /api/v1/tree/conflicts/orphans, /api/v1/tree/conflicts/orphans, /tree/conflicts/orphans, /tree/conflicts/orphans |
| /tree/conflicts/parent/{parent_id}/merge-duplicates | OK | /api/v1/tree/conflicts/parent/{parent_id}/merge-duplicates, /tree/conflicts/parent/{parent_id}/merge-duplicates |
| /tree/conflicts/parent/{parent_id}/normalize | OK | /api/v1/tree/conflicts/parent/{parent_id}/normalize, /tree/conflicts/parent/{parent_id}/normalize |
| /tree/export | OK | /api/v1/tree/export, /tree/export |
| /tree/export-json | OK | /api/v1/tree/export-json, /tree/export-json |
| /tree/export.xlsx | OK | /api/v1/tree/export.xlsx, /tree/export.xlsx |
| /tree/labels | OK | /api/v1/tree/labels, /tree/labels |
| /tree/labels/{label}/aggregate | OK | /api/v1/tree/labels/{label}/aggregate, /tree/labels/{label}/aggregate |
| /tree/labels/{label}/apply-default | OK | /api/v1/tree/labels/{label}/apply-default, /tree/labels/{label}/apply-default |
| /tree/leaves | OK | /api/v1/tree/leaves, /tree/leaves |
| /tree/materialize | OK | /api/v1/tree/materialize, /tree/materialize |
| /tree/materialize/runs | OK | /api/v1/tree/materialize/runs, /tree/materialize/runs |
| /tree/materialize/undo | OK | /api/v1/tree/materialize/undo, /tree/materialize/undo |
| /tree/missing-slots | OK | /api/v1/tree/missing-slots, /api/v1/tree/missing-slots, /tree/missing-slots, /tree/missing-slots |
| /tree/missing-slots-json | OK | /api/v1/tree/missing-slots-json, /tree/missing-slots-json |
| /tree/navigate | OK | /api/v1/tree/navigate, /tree/navigate |
| /tree/next-incomplete-parent | OK | /api/v1/tree/next-incomplete-parent, /api/v1/tree/next-incomplete-parent, /api/v1/tree/next-incomplete-parent, /tree/next-incomplete-parent, /tree/next-incomplete-parent, /tree/next-incomplete-parent |
| /tree/next-incomplete-parent-json | OK | /api/v1/tree/next-incomplete-parent-json, /tree/next-incomplete-parent-json |
| /tree/parent/{parent_id:int}/children | OK | /api/v1/tree/parent/{parent_id:int}/children, /api/v1/tree/parent/{parent_id:int}/children, /tree/parent/{parent_id:int}/children, /tree/parent/{parent_id:int}/children |
| /tree/parents | OK | /api/v1/tree/parents, /tree/parents |
| /tree/parents/incomplete | OK | /api/v1/tree/parents/incomplete, /tree/parents/incomplete |
| /tree/path | OK | /api/v1/tree/path, /tree/path |
| /tree/root-options | OK | /api/v1/tree/root-options, /tree/root-options |
| /tree/roots | OK | /api/v1/tree/roots, /api/v1/tree/roots, /api/v1/tree/roots, /tree/roots, /tree/roots, /tree/roots |
| /tree/stats | OK | /api/v1/tree/stats, /api/v1/tree/stats, /tree/stats, /tree/stats |
| /tree/suggest/labels | OK | /api/v1/tree/suggest/labels, /tree/suggest/labels |
| /tree/vm | OK | /api/v1/tree/vm, /tree/vm |
| /tree/wizard/sheet | OK | /api/v1/tree/wizard/sheet, /tree/wizard/sheet |
| /tree/wizard/sheet/commit | OK | /api/v1/tree/wizard/sheet/commit, /tree/wizard/sheet/commit |
| /tree/{node_id} | OK | /api/v1/tree/{node_id}, /tree/{node_id} |
| /tree/{parent_id:int} | OK | /api/v1/tree/{parent_id:int}, /tree/{parent_id:int} |
| /tree/{parent_id:int}/child | OK | /api/v1/tree/{parent_id:int}/child, /tree/{parent_id:int}/child |
| /tree/{parent_id:int}/children | OK | /api/v1/tree/{parent_id:int}/children, /api/v1/tree/{parent_id:int}/children, /api/v1/tree/{parent_id:int}/children, /api/v1/tree/{parent_id:int}/children, /tree/{parent_id:int}/children, /tree/{parent_id:int}/children, /tree/{parent_id:int}/children, /tree/{parent_id:int}/children |
| /tree/{parent_id:int}/slot/{slot:int} | OK | /api/v1/tree/{parent_id:int}/slot/{slot:int}, /api/v1/tree/{parent_id:int}/slot/{slot:int}, /tree/{parent_id:int}/slot/{slot:int}, /tree/{parent_id:int}/slot/{slot:int} |
| /tree/{parent_id}/slot/{slot} | OK | /api/v1/tree/{parent_id}/slot/{slot}, /tree/{parent_id}/slot/{slot} |
| /triage/search | OK | /api/v1/triage/search, /triage/search |
| /triage/{node_id:int} | OK | /api/v1/triage/{node_id:int}, /api/v1/triage/{node_id:int}, /triage/{node_id:int}, /triage/{node_id:int} |


## Flutter API URLs discovered

| URL / Path |
| --- |
| $base/calc/export?vm=BP&n1=Pain&n2=Sharp... |
| ${widget.baseUrl}/api/v1/admin/clear-nodes |
| ${widget.baseUrl}/api/v1/admin/clear?include_dictionary=${_includeDictionary.toString()} |
| ${widget.baseUrl}/api/v1/import/preview |
| ${widget.baseUrl}/api/v1/tree/$pid |
| ${widget.baseUrl}/api/v1/tree/$pid/slot/$slot |
| ${widget.baseUrl}/api/v1/tree/children/$parentId |
| ${widget.baseUrl}/api/v1/tree/children?parent_id=$parentId |
| ${widget.baseUrl}/api/v1/tree/conflicts/conflicts?limit=50&offset=0 |
| ${widget.baseUrl}/api/v1/tree/conflicts/group/resolve |
| ${widget.baseUrl}/api/v1/tree/conflicts/group?node_id=$nodeId |
| ${widget.baseUrl}/api/v1/tree/conflicts/parent/$parentId/normalize |
| ${widget.baseUrl}/api/v1/tree/export-json?limit=$_pageSize&offset=$_offset |
| ${widget.baseUrl}/api/v1/tree/labels |
| ${widget.baseUrl}/api/v1/tree/labels/${Uri.encodeComponent(label)}/aggregate |
| ${widget.baseUrl}/api/v1/tree/labels/${Uri.encodeComponent(label)}/apply-default |
| ${widget.baseUrl}/api/v1/tree/leaves?limit=100&offset=0 |
| ${widget.baseUrl}/api/v1/tree/missing-slots-json?limit=$_pageSize&offset=$_offset |
| ${widget.baseUrl}/api/v1/tree/missing-slots-json?limit=100&offset=0 |
| ${widget.baseUrl}/api/v1/tree/navigate |
| ${widget.baseUrl}/api/v1/tree/next-incomplete-parent-json |
| ${widget.baseUrl}/api/v1/tree/parents |
| ${widget.baseUrl}/api/v1/tree/root-options |
| ${widget.baseUrl}/api/v1/tree/roots?limit=100&offset=0 |
| ${widget.baseUrl}/api/v1/tree/stats |
| ${widget.baseUrl}/api/v1/tree/vm |


## Flutter pushNamed routes

| Route |
| --- |
| /edit-tree |


## Pytest summary

```
ext_incomplete.py:10: in <module>
    from core.services.tree_service import TreeService
E   ImportError: cannot import name 'TreeService' from 'core.services.tree_service' (/home/jharm/Lorien/core/services/tree_service.py)
=============================== warnings summary ===============================
venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
  /home/jharm/Lorien/venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

api/app.py:202
  /home/jharm/Lorien/api/app.py:202: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

venv/lib/python3.12/site-packages/fastapi/applications.py:4495
  /home/jharm/Lorien/venv/lib/python3.12/site-packages/fastapi/applications.py:4495: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    return self.router.on_event(event_type)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
ERROR tests/e2e/test_conflicts_concurrency.py
ERROR tests/e2e/test_performance_smoke.py
ERROR tests/e2e/test_roundtrip.py
ERROR tests/ops/test_prune_flags.py
ERROR tests/test_edit_tree.py
ERROR tests/test_outcomes_validation.py
ERROR tests/unit/test_next_incomplete.py
!!!!!!!!!!!!!!!!!!! Interrupted: 7 errors during collection !!!!!!!!!!!!!!!!!!!!

```
