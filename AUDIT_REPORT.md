# Wiring Audit Report

Generated: `2025-09-08T20:07:51Z`

## Backend routes (sample)
| Path | Methods | Name |
| --- | --- | --- |
| / | GET | root |
| /admin/clear | POST | admin_clear |
| /admin/clear-nodes | POST | clear_nodes_endpoint |
| /admin/hard-reset-nodes | POST | hard_reset_nodes_endpoint |
| /admin/roots/suspect | GET | suspect_roots |
| /admin/sanitize-labels | POST | sanitize_labels |
| /admin/search-test-labels | GET | search_test_labels |
| /admin/sync-dictionary-from-tree | POST | sync_dictionary_from_tree |
| /api/v1/ | GET | root |
| /api/v1/admin/clear | POST | admin_clear |
| /api/v1/admin/clear-nodes | POST | clear_nodes_endpoint |
| /api/v1/admin/hard-reset-nodes | POST | hard_reset_nodes_endpoint |
| /api/v1/admin/roots/suspect | GET | suspect_roots |
| /api/v1/admin/sanitize-labels | POST | sanitize_labels |
| /api/v1/admin/search-test-labels | GET | search_test_labels |
| /api/v1/admin/sync-dictionary-from-tree | POST | sync_dictionary_from_tree |
| /api/v1/backup | POST | create_backup |
| /api/v1/backup/status | GET | get_backup_status |
| /api/v1/calc/export | GET | export_calculator_csv |
| /api/v1/calc/export.xlsx | GET | export_calculator_xlsx |
| /api/v1/dictionary | GET | list_terms |
| /api/v1/dictionary | POST | create_term |
| /api/v1/dictionary/export | GET | dictionary_export_csv |
| /api/v1/dictionary/export.xlsx | GET | dictionary_export_xlsx |
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
| /api/v1/tree/export | GET | export_csv |
| /api/v1/tree/export-json | GET | tree_export |
| /api/v1/tree/export.xlsx | GET | export_xlsx |
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
| /api/v1/tree/parents/query | GET | parents_query_endpoint |
| /api/v1/tree/path | GET | get_node_path |
| /api/v1/tree/progress | GET | tree_progress |
| /api/v1/tree/root-options | GET | get_root_options |
| /api/v1/tree/roots | GET | get_roots |
| /api/v1/tree/roots | POST | create_vital_measurement |
| /api/v1/tree/roots | GET | list_roots |
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
| /api/v1/tree/{parent_id:int}/children | POST | upsert_children |
| /api/v1/tree/{parent_id:int}/children | GET | get_parent_children |
| /api/v1/tree/{parent_id:int}/children | POST | bulk_update_children |
| /api/v1/tree/{parent_id:int}/slot/{slot:int} | PUT | upsert_slot |
| /api/v1/tree/{parent_id:int}/slot/{slot:int} | DELETE | delete_slot |
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
| /dictionary/export | GET | dictionary_export_csv |
| /dictionary/export.xlsx | GET | dictionary_export_xlsx |
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
| /tree/export | GET | export_csv |
| /tree/export-json | GET | tree_export |
| /tree/export.xlsx | GET | export_xlsx |
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
| /tree/parents/query | GET | parents_query_endpoint |
| /tree/path | GET | get_node_path |
| /tree/progress | GET | tree_progress |
| /tree/root-options | GET | get_root_options |
| /tree/roots | GET | get_roots |
| /tree/roots | POST | create_vital_measurement |
| /tree/roots | GET | list_roots |
| /tree/stats | GET | tree_stats |
| /tree/stats | GET | get_tree_stats |
| /tree/suggest/labels | GET | suggest_labels |
| /tree/vm | POST | create_vm |
| /tree/wizard/sheet | POST | stage_sheet_wizard |
| /tree/wizard/sheet/commit | POST | commit_sheet_wizard |
| /tree/{node_id} | DELETE | delete_parent |

## Dual-mount compliance
| Base Path | Bare | v1 | Example(s) |
| --- | --- | --- | --- |
| / | True | True | /, /api/v1/ |
| /admin/clear | True | True | /api/v1/admin/clear, /admin/clear |
| /admin/clear-nodes | True | True | /api/v1/admin/clear-nodes, /admin/clear-nodes |
| /admin/hard-reset-nodes | True | True | /api/v1/admin/hard-reset-nodes, /admin/hard-reset-nodes |
| /admin/roots/suspect | True | True | /api/v1/admin/roots/suspect, /admin/roots/suspect |
| /admin/sanitize-labels | True | True | /api/v1/admin/sanitize-labels, /admin/sanitize-labels |
| /admin/search-test-labels | True | True | /api/v1/admin/search-test-labels, /admin/search-test-labels |
| /admin/sync-dictionary-from-tree | True | True | /api/v1/admin/sync-dictionary-from-tree, /admin/sync-dictionary-from-tree |
| /backup | True | True | /api/v1/backup, /backup |
| /backup/status | True | True | /api/v1/backup/status, /backup/status |
| /calc/export | True | True | /api/v1/calc/export, /calc/export |
| /calc/export.xlsx | True | True | /api/v1/calc/export.xlsx, /calc/export.xlsx |
| /dictionary | True | True | /api/v1/dictionary, /api/v1/dictionary |
| /dictionary/export | True | True | /api/v1/dictionary/export, /dictionary/export |
| /dictionary/export.xlsx | True | True | /api/v1/dictionary/export.xlsx, /dictionary/export.xlsx |
| /dictionary/normalize | True | True | /api/v1/dictionary/normalize, /dictionary/normalize |
| /flags | True | True | /api/v1/flags, /flags |
| /flags/assign | True | True | /api/v1/flags/assign, /api/v1/flags/assign |
| /flags/audit | True | True | /api/v1/flags/audit, /flags/audit |
| /flags/audit/ | True | True | /api/v1/flags/audit/, /api/v1/flags/audit/ |
| /flags/preview-assign | True | True | /api/v1/flags/preview-assign, /flags/preview-assign |
| /flags/remove | True | True | /api/v1/flags/remove, /api/v1/flags/remove |
| /flags/search | True | True | /api/v1/flags/search, /flags/search |
| /health | True | True | /api/v1/health, /health |
| /health/metrics | True | True | /api/v1/health/metrics, /health/metrics |
| /import | True | True | /api/v1/import, /import |
| /import/excel | True | True | /api/v1/import/excel, /import/excel |
| /import/jobs | True | True | /api/v1/import/jobs, /import/jobs |
| /import/jobs/{job_id:int} | True | True | /api/v1/import/jobs/{job_id:int}, /import/jobs/{job_id:int} |
| /import/preview | True | True | /api/v1/import/preview, /import/preview |
| /llm/fill-triage-actions | True | True | /api/v1/llm/fill-triage-actions, /llm/fill-triage-actions |
| /llm/health | True | True | /api/v1/llm/health, /llm/health |
| /outcomes/triage/{node_id:int} | True | True | /api/v1/outcomes/triage/{node_id:int}, /outcomes/triage/{node_id:int} |
| /outcomes/{node_id:int} | True | True | /api/v1/outcomes/{node_id:int}, /outcomes/{node_id:int} |
| /red-flags/audit | True | True | /api/v1/red-flags/audit, /red-flags/audit |
| /red-flags/bulk-attach | True | True | /api/v1/red-flags/bulk-attach, /red-flags/bulk-attach |
| /red-flags/bulk-detach | True | True | /api/v1/red-flags/bulk-detach, /red-flags/bulk-detach |
| /restore | True | True | /api/v1/restore, /restore |
| /tree/children | True | True | /api/v1/tree/children, /tree/children |
| /tree/children/{parent_id} | True | True | /api/v1/tree/children/{parent_id}, /tree/children/{parent_id} |
| /tree/conflicts | True | True | /tree/conflicts, /api/v1/tree/conflicts |
| /tree/conflicts/conflicts | True | True | /api/v1/tree/conflicts/conflicts, /tree/conflicts/conflicts |
| /tree/conflicts/depth-anomalies | True | True | /api/v1/tree/conflicts/depth-anomalies, /api/v1/tree/conflicts/depth-anomalies |
| /tree/conflicts/duplicate-labels | True | True | /api/v1/tree/conflicts/duplicate-labels, /api/v1/tree/conflicts/duplicate-labels |
| /tree/conflicts/group | True | True | /api/v1/tree/conflicts/group, /tree/conflicts/group |
| /tree/conflicts/group/resolve | True | True | /api/v1/tree/conflicts/group/resolve, /tree/conflicts/group/resolve |
| /tree/conflicts/orphans | True | True | /api/v1/tree/conflicts/orphans, /api/v1/tree/conflicts/orphans |
| /tree/conflicts/parent/{parent_id}/merge-duplicates | True | True | /api/v1/tree/conflicts/parent/{parent_id}/merge-duplicates, /tree/conflicts/parent/{parent_id}/merge-duplicates |
| /tree/conflicts/parent/{parent_id}/normalize | True | True | /api/v1/tree/conflicts/parent/{parent_id}/normalize, /tree/conflicts/parent/{parent_id}/normalize |
| /tree/export | True | True | /api/v1/tree/export, /api/v1/tree/export |
| /tree/export-json | True | True | /api/v1/tree/export-json, /tree/export-json |
| /tree/export.xlsx | True | True | /api/v1/tree/export.xlsx, /api/v1/tree/export.xlsx |
| /tree/labels | True | True | /api/v1/tree/labels, /tree/labels |
| /tree/labels/{label}/aggregate | True | True | /api/v1/tree/labels/{label}/aggregate, /tree/labels/{label}/aggregate |
| /tree/labels/{label}/apply-default | True | True | /api/v1/tree/labels/{label}/apply-default, /tree/labels/{label}/apply-default |
| /tree/leaves | True | True | /api/v1/tree/leaves, /tree/leaves |
| /tree/materialize | True | True | /api/v1/tree/materialize, /tree/materialize |
| /tree/materialize/runs | True | True | /api/v1/tree/materialize/runs, /tree/materialize/runs |
| /tree/materialize/undo | True | True | /api/v1/tree/materialize/undo, /tree/materialize/undo |
| /tree/missing-slots | True | True | /api/v1/tree/missing-slots, /api/v1/tree/missing-slots |
| /tree/missing-slots-json | True | True | /api/v1/tree/missing-slots-json, /tree/missing-slots-json |
| /tree/navigate | True | True | /api/v1/tree/navigate, /tree/navigate |
| /tree/next-incomplete-parent | True | True | /api/v1/tree/next-incomplete-parent, /api/v1/tree/next-incomplete-parent |
| /tree/next-incomplete-parent-json | True | True | /api/v1/tree/next-incomplete-parent-json, /tree/next-incomplete-parent-json |
| /tree/parent/{parent_id:int}/children | True | True | /api/v1/tree/parent/{parent_id:int}/children, /api/v1/tree/parent/{parent_id:int}/children |
| /tree/parents | True | True | /api/v1/tree/parents, /tree/parents |
| /tree/parents/incomplete | True | True | /api/v1/tree/parents/incomplete, /tree/parents/incomplete |
| /tree/parents/query | True | True | /api/v1/tree/parents/query, /tree/parents/query |
| /tree/path | True | True | /api/v1/tree/path, /tree/path |
| /tree/progress | True | True | /api/v1/tree/progress, /tree/progress |
| /tree/root-options | True | True | /api/v1/tree/root-options, /tree/root-options |
| /tree/roots | True | True | /api/v1/tree/roots, /api/v1/tree/roots |
| /tree/stats | True | True | /api/v1/tree/stats, /api/v1/tree/stats |
| /tree/suggest/labels | True | True | /api/v1/tree/suggest/labels, /tree/suggest/labels |
| /tree/vm | True | True | /api/v1/tree/vm, /tree/vm |
| /tree/wizard/sheet | True | True | /api/v1/tree/wizard/sheet, /tree/wizard/sheet |
| /tree/wizard/sheet/commit | True | True | /api/v1/tree/wizard/sheet/commit, /tree/wizard/sheet/commit |
| /tree/{node_id} | True | True | /api/v1/tree/{node_id}, /tree/{node_id} |
| /tree/{parent_id:int} | True | True | /api/v1/tree/{parent_id:int}, /tree/{parent_id:int} |
| /tree/{parent_id:int}/child | True | True | /api/v1/tree/{parent_id:int}/child, /tree/{parent_id:int}/child |
| /tree/{parent_id:int}/children | True | True | /api/v1/tree/{parent_id:int}/children, /api/v1/tree/{parent_id:int}/children |
| /tree/{parent_id:int}/slot/{slot:int} | True | True | /api/v1/tree/{parent_id:int}/slot/{slot:int}, /api/v1/tree/{parent_id:int}/slot/{slot:int} |
| /tree/{parent_id}/slot/{slot} | True | True | /api/v1/tree/{parent_id}/slot/{slot}, /tree/{parent_id}/slot/{slot} |
| /triage/search | True | True | /api/v1/triage/search, /triage/search |
| /triage/{node_id:int} | True | True | /api/v1/triage/{node_id:int}, /api/v1/triage/{node_id:int} |

All routes dual-mounted ✅

## Required features coverage
All required endpoints present ✅

## Flutter scan
### API URLs discovered
- `/$`
- `/$fileName`
- `/$fname`
- `/$id`
- `/$max`
- `/$nodeId`
- `/$p`
- `/$parentId/child`
- `/$parentId/children`
- `/+`
- `/+$`
- `/../../api/lorien_api.dart`
- `/../../core/api_config.dart`
- `/../../core/http/api_client.dart`
- `/../../core/services/health_service.dart`
- `/../../core/util/error_mapper.dart`
- `/../../core/validators/field_validators.dart`
- `/../../data/api_client.dart`
- `/../../data/dto/child_slot_dto.dart`
- `/../../features/tree/data/tree_api.dart`
- `/../../features/workspace/calculator_screen.dart`
- `/../../providers/lorien_api_provider.dart`
- `/../../shared/widgets/app_scaffold.dart`
- `/../../shared/widgets/connected_badge.dart`
- `/../../shared/widgets/field_error_text.dart`
- `/../../shared/widgets/route_guard.dart`
- `/../../shared/widgets/scroll_to_top_fab.dart`
- `/../../shared/widgets/toasts.dart`
- `/../../state/health_provider.dart`
- `/../../widgets/app_back_leading.dart`
- `/../../widgets/calc_export_dialog.dart`
- `/../../widgets/layout/scroll_scaffold.dart`
- `/../api/lorien_api.dart`
- `/../core/api_config.dart`
- `/../core/crash_report_service.dart`
- `/../core/services/health_service.dart`
- `/../core/widgets/keep_alive.dart`
- `/../data/api_client.dart`
- `/../data/dto/child_slot_dto.dart`
- `/../data/triage_repository.dart`
- `/../dictionary/ui/dictionary_suggestions_overlay.dart`
- `/../features/dictionary/ui/dictionary_screen.dart`
- `/../features/flags/ui/flags_screen.dart`
- `/../features/home/ui/home_screen.dart`
- `/../features/outcomes/ui/outcomes_detail_screen.dart`
- `/../features/outcomes/ui/outcomes_list_screen.dart`
- `/../features/settings/ui/about_status_page.dart`
- `/../features/settings/ui/settings_screen.dart`
- `/../features/workspace/conflicts_screen.dart`
- `/../features/workspace/edit_tree_screen.dart`
- `/../features/workspace/stats_details_screen.dart`
- `/../features/workspace/ui/workspace_screen.dart`
- `/../features/workspace/vm_builder_screen.dart`
- `/../models/triage_models.dart`
- `/../providers/lorien_api_provider.dart`
- `/../providers/settings_provider.dart`
- `/../services/telemetry_client.dart`
- `/../state/action_providers.dart`
- `/../state/app_settings_provider.dart`
- `/../state/flags_search_provider.dart`
- `/../state/health_provider.dart`
- `/../state/repository_providers.dart`
- `/../symptoms/data/materialization_service.dart`
- `/../widgets/app_back_leading.dart`
- `/../widgets/layout/scroll_scaffold.dart`
- `/.csv)`
- `//10.0.2.2:8000/api/v1`
- `//127.0.0.1:8000`
- `//127.0.0.1:8000/api/v1`
- `//192.168.1.100:8000/api/v1`
- `//192.168.1.xxx:8000/api/v1`
- `//<LAN-IP>:8000/api/v1`
- `//<LAN-IP>:<port>`
- `//api.example.com/api/v1`
- `//api.lorien.example.com/api/v1`
- `//github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models`
- `//localhost:8000`
- `//localhost:8000/api/v1`
- `/5`
- `/5):`
- `/7`
- `/A`
- `/CSV`
- `/Desktop:`
- `/Network`
- `/about`
- `/admin/clear-nodes`
- `/api/dictionary_api.dart`
- `/api/health_api.dart`
- `/api/import_api.dart`
- `/api/lorien_api.dart`
- `/api/outcomes_api.dart`
- `/api/tree_api.dart`
- `/api/v1/`
- `/api/v1/?$`
- `/api/v1/admin/clear-nodes`
- `/api/v1/admin/clear?include_dictionary=${_includeDictionary.toString()}`
- `/api/v1/dictionary/export`
- `/api/v1/dictionary/export(.xlsx)`
- `/api/v1/dictionary/export.xlsx`
- `/api/v1/import/preview`
- `/api/v1/tree/$nodeId`
- `/api/v1/tree/$pid`
- `/api/v1/tree/$pid/slot/$slot`
- `/api/v1/tree/children/$parentId`
- `/api/v1/tree/children?parent_id=$parentId`
- `/api/v1/tree/conflicts/conflicts?limit=50&offset=0`
- `/api/v1/tree/conflicts/group/resolve`
- `/api/v1/tree/conflicts/group?node_id=$nodeId`
- `/api/v1/tree/conflicts/parent/$parentId/normalize`
- `/api/v1/tree/export`
- `/api/v1/tree/export-json?limit=$_limit&offset=$_offset`
- `/api/v1/tree/export-json?limit=$_pageSize&offset=$_offset`
- `/api/v1/tree/export.xlsx`
- `/api/v1/tree/labels`
- `/api/v1/tree/labels/${Uri.encodeComponent(label)}/aggregate`
- `/api/v1/tree/labels/${Uri.encodeComponent(label)}/apply-default`
- `/api/v1/tree/leaves?limit=$_limit&offset=$_offset&q=$qstr`
- `/api/v1/tree/missing-slots-json?limit=$_pageSize&offset=$_offset`
- `/api/v1/tree/navigate`
- `/api/v1/tree/next-incomplete-parent-json`
- `/api/v1/tree/parents`
- `/api/v1/tree/parents/query?filter=complete5&limit=$_limit&offset=$_offset&q=$qstr`
- `/api/v1/tree/parents/query?filter=complete_diff&limit=$_limit&offset=$_offset&q=$qstr`
- `/api/v1/tree/parents/query?filter=complete_same&limit=$_limit&offset=$_offset&q=$qstr`
- `/api/v1/tree/parents/query?filter=incomplete_lt4&limit=$_limit&offset=$_offset&q=$qstr`
- `/api/v1/tree/parents/query?filter=saturated&limit=$_limit&offset=$_offset&q=$qstr`
- `/api/v1/tree/root-options`
- `/api/v1/tree/root-options?limit=$_limit&offset=$_offset&q=$qstr`
- `/api/v1/tree/stats`
- `/api/v1/tree/vm`
- `/api_client.dart`
- `/api_paths.dart`
- `/app.log`
- `/app_router.dart`
- `/app_scroll_behavior.dart`
- `/app_settings_provider.dart`
- `/app_theme.dart`
- `/assign`
- `/assign/bulk`
- `/bug`
- `/calc/export`
- `/calc/export.xlsx`
- `/calc/export?vm=BP&n1=Pain&n2=Sharp...`
- `/calc/options`
- `/children`
- `/conflicts`
- `/connectivity_plus.dart`
- `/core/api_config.dart`
- `/core/services/health_service.dart`
- `/crash`
- `/crash_report_service.dart`
- `/cross_file.dart`
- `/csv`
- `/data/api_client.dart`
- `/data/conflicts_models.dart`
- `/data/conflicts_service.dart`
- `/data/dictionary_repository.dart`
- `/data/dto/child_slot_dto.dart`
- `/data/dto/children_upsert_dto.dart`
- `/data/dto/incomplete_parent_dto.dart`
- `/data/dto/triage_dto.dart`
- `/data/edit_tree_provider.dart`
- `/data/edit_tree_repository.dart`
- `/data/flags_api.dart`
- `/data/llm_api.dart`
- `/data/materialization_service.dart`
- `/data/outcomes_api.dart`
- `/data/repos/calc_repository.dart`
- `/data/repos/flags_repository.dart`
- `/data/repos/tree_repository.dart`
- `/data/repos/triage_repository.dart`
- `/data/session_models.dart`
- `/data/session_service.dart`
- `/data/symptoms_models.dart`
- `/data/symptoms_repository.dart`
- `/data/vm_builder_models.dart`
- `/data/vm_builder_service.dart`
- `/data/workspace_models.dart`
- `/diagnosis.`
- `/dictionary`
- `/dictionary/`
- `/dictionary/$id`
- `/dictionary/normalize`
- `/dio.dart`
- `/downloads/$fileName`
- `/dto/child_slot_dto.dart`
- `/dto/children_upsert_dto.dart`
- `/dto/incomplete_parent_dto.dart`
- `/dto/triage_dto.dart`
- `/edit-tree`
- `/editor`
- `/editor/parent/${nextIncomplete.parentId}`
- `/export`
- `/export.xlsx`
- `/export/csv`
- `/export_panel.dart`
- `/fake/db/path`
- `/features/dictionary/data/dictionary_repository.dart`
- `/features/dictionary/ui/dictionary_screen.dart`
- `/features/edit_tree/ui/edit_tree_screen.dart`
- `/features/flags/ui/flags_screen.dart`
- `/features/symptoms/data/symptoms_repository.dart`
- `/features/workspace/calculator_screen.dart`
- `/features/workspace/ui/workspace_screen.dart`
- `/file_picker.dart`
- `/file_selector.dart`
- `/fill-triage-actions`
- `/flags`
- `/flags/assign`
- `/flags/audit`
- `/flags/preview-assign`
- `/flags/remove`
- `/flutter_riverpod.dart`
- `/form-data`
- `/foundation.dart`
- `/freezed_annotation.dart`
- `/gestures.dart`
- `/go_router.dart`
- `/health`
- `/health)`
- `/home`
- `/http.dart`
- `/http/api_client.dart`
- `/http_parser.dart`
- `/import`
- `/import/excel`
- `/json`
- `/llm/fill-triage-actions`
- `/llm/health`
- `/lorien_calc_export_$timestamp.csv`
- `/lorien_tree_export_$timestamp.xlsx`
- `/material.dart`
- `/metrics/event`
- `/missing-slots`
- `/models/triage_models.dart`
- `/network/dio_api_client.dart`
- `/network/fake_api_client.dart`
- `/next-incomplete-parent`
- `/normalize`
- `/outcomes`
- `/outcomes/$id`
- `/outcomes/:id`
- `/parent/$parentId/children`
- `/path`
- `/path_provider.dart`
- `/pretty_dio_logger.dart`
- `/progress`
- `/provider.dart`
- `/roots`
- `/router/app_router.dart`
- `/screens/about/about_screen.dart`
- `/screens/settings_screen.dart`
- `/search`
- `/services.dart`
- `/services/health_service.dart`
- `/session/csv-import`
- `/session/csv-preview`
- `/session/current`
- `/session/export`
- `/session/import`
- `/session/import-conflicts`
- `/session/push-log`
- `/session/resolve-conflicts`
- `/session/sheets`
- `/session/sheets/$sheetId/metadata`
- `/session/suggest-headers`
- `/session/switch-sheet`
- `/session/validate-import`
- `/session/workbooks`
- `/session/workbooks/$workbookId`
- `/settings`
- `/settings/logic/settings_controller.dart`
- `/share_plus.dart`
- `/shared_preferences.dart`
- `/state/app_settings_provider.dart`
- `/state/edit_tree_controller.dart`
- `/state/edit_tree_state.dart`
- `/stats`
- `/stats-details`
- `/stats_details_screen.dart`
- `/sync-dictionary-from-tree`
- `/tree-navigator`
- `/tree/`
- `/tree/$parentId/children`
- `/tree/conflicts`
- `/tree/conflicts/$conflictId`
- `/tree/conflicts/$conflictId/location`
- `/tree/conflicts/$conflictId/suggestions`
- `/tree/conflicts/${resolution.conflictId}/resolve`
- `/tree/conflicts/${type.name}`
- `/tree/conflicts/auto-resolve`
- `/tree/conflicts/batch-resolve`
- `/tree/conflicts/summary`
- `/tree/export`
- `/tree/export.xlsx`
- `/tree/materialization-history`
- `/tree/materialization-stats`
- `/tree/materialize-all`
- `/tree/materialize-batch`
- `/tree/next-incomplete-parent`
- `/tree/parent/$parentId/batch-add`
- `/tree/parent/$parentId/children`
- `/tree/parent/$parentId/materialize`
- `/tree/parent/$parentId/materialize-preview`
- `/tree/parents/incomplete`
- `/tree/roots`
- `/tree/stats`
- `/tree/undo-last-materialization`
- `/triage/`
- `/triage/$leafId`
- `/triage/$nodeId`
- `/triage/${widget.outcomeId}`
- `/triage/actions)…`
- `/triage/search`
- `/utils/env.dart`
- `/uuid.dart`
- `/v1`
- `/vm-builder`
- `/vm-builder/check-duplicates`
- `/vm-builder/common-prefixes`
- `/vm-builder/create`
- `/vm-builder/suggestions`
- `/vm-builder/templates`
- `/vm-builder/templates/$templateId`
- `/vm-builder/validate`
- `/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- `/widgets.dart`
- `/widgets/app_back_leading.dart`
- `/widgets/layout/scroll_scaffold.dart`
- `/widgets/nav_shortcuts.dart`
- `/workspace`
- `/workspace/backup`
- `/workspace/integrity-check`
- `/workspace/restore`
- `/xlsx`

### pushNamed routes
- `/edit-tree`

### UI presence check
All expected UI actions/texts found in Flutter sources ✅

## Pytest summary

```
==================================== ERRORS ====================================
___________ ERROR collecting tests/e2e/test_conflicts_concurrency.py ___________
ImportError while importing test module '/home/jharm/Lorien/tests/e2e/test_conflicts_concurrency.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/e2e/test_conflicts_concurrency.py:9: in <module>
    from tests.utils.http import get_json, post_json
E   ModuleNotFoundError: No module named 'tests'
_____________ ERROR collecting tests/e2e/test_performance_smoke.py _____________
ImportError while importing test module '/home/jharm/Lorien/tests/e2e/test_performance_smoke.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/e2e/test_performance_smoke.py:9: in <module>
    from tests.utils.http import get_json
E   ModuleNotFoundError: No module named 'tests'
_________________ ERROR collecting tests/e2e/test_roundtrip.py _________________
ImportError while importing test module '/home/jharm/Lorien/tests/e2e/test_roundtrip.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/e2e/test_roundtrip.py:10: in <module>
    from tests.utils.csv_compare import assert_csv_equal
E   ModuleNotFoundError: No module named 'tests'
________________ ERROR collecting tests/ops/test_prune_flags.py ________________
venv/lib/python3.12/site-packages/_pytest/python.py:498: in importtestmodule
    mod = import_path(
venv/lib/python3.12/site-packages/_pytest/pathlib.py:587: in import_path
    importlib.import_module(module_name)
/usr/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
<frozen importlib._bootstrap>:1331: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:935: in _load_unlocked
    ???
venv/lib/python3.12/site-packages/_pytest/assertion/rewrite.py:186: in exec_module
    exec(co, module.__dict__)
tests/ops/test_prune_flags.py:10: in <module>
    from ops.prune_flags import prune_flag_audit
E     File "/home/jharm/Lorien/ops/prune_flags.py", line 169
E       print("✅ Pruning completed successfully"            print(f"   Rows before: {result.get('rows_before', 0):,}")
E            ^
E   SyntaxError: '(' was never closed
_____________ ERROR collecting tests/test_core_endpoints_exist.py ______________
ImportError while importing test module '/home/jharm/Lorien/tests/test_core_endpoints_exist.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_core_endpoints_exist.py:1: in <module>
    from tools.audit.wiring_audit import collect_routes
tools/audit/wiring_audit.py:6: in <module>
    from _util import import_fastapi_app, ROUTE_EXCLUDES
E   ImportError: cannot import name 'import_fastapi_app' from '_util' (/home/jharm/Lorien/tools/audit/_util.py)
______________ ERROR collecting tests/test_dual_mount_contract.py ______________
ImportError while importing test module '/home/jharm/Lorien/tests/test_dual_mount_contract.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_dual_mount_contract.py:1: in <module>
    from tools.audit.check_dual_mount import run_check
tools/audit/check_dual_mount.py:7: in <module>
    from wiring_audit import collect_routes, map_dual_mount
tools/audit/wiring_audit.py:6: in <module>
    from _util import import_fastapi_app, ROUTE_EXCLUDES
E   ImportError: cannot import name 'import_fastapi_app' from '_util' (/home/jharm/Lorien/tools/audit/_util.py)
___________________ ERROR collecting tests/test_edit_tree.py ___________________
import file mismatch:
imported module 'test_edit_tree' has this __file__ attribute:
  /home/jharm/Lorien/tests/api/test_edit_tree.py
which is not the same as the test file we want to collect:
  /home/jharm/Lorien/tests/test_edit_tree.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
______________ ERROR collecting tests/test_outcomes_validation.py ______________
import file mismatch:
imported module 'test_outcomes_validation' has this __file__ attribute:
  /home/jharm/Lorien/tests/api/test_outcomes_validation.py
which is not the same as the test file we want to collect:
  /home/jharm/Lorien/tests/test_outcomes_validation.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
_____________ ERROR collecting tests/unit/test_next_incomplete.py ______________
ImportError while importing test module '/home/jharm/Lorien/tests/unit/test_next_incomplete.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_next_incomplete.py:10: in <module>
    from core.services.tree_service import TreeService
E   ImportError: cannot import name 'TreeService' from 'core.services.tree_service' (/home/jharm/Lorien/core/services/tree_service.py)
=============================== warnings summary ===============================
venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
  /home/jharm/Lorien/venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

api/app.py:205
  /home/jharm/Lorien/api/app.py:205: DeprecationWarning: 
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
ERROR tests/test_core_endpoints_exist.py
ERROR tests/test_dual_mount_contract.py
ERROR tests/test_edit_tree.py
ERROR tests/test_outcomes_validation.py
ERROR tests/unit/test_next_incomplete.py
!!!!!!!!!!!!!!!!!!! Interrupted: 9 errors during collection !!!!!!!!!!!!!!!!!!!!
```