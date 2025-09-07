# Lorien Wiring Map

## Overview
This document maps the flow from UI components through repositories to API endpoints, highlighting broken connections and implementation gaps.

## Flow 1: Edit Tree → Next Incomplete Parent
```
UI: EditTreeScreen.nextIncompleteButton.onPressed
    ↓
Repository: EditTreeRepository.fetchNextIncompleteParent()
    ↓
HTTP: GET /api/v1/tree/next-incomplete-parent
    ↓
Router: tree.py::next_incomplete_parent()
    ↓
DB: Query incomplete parents
```

**Status**: 🔴 BROKEN
**Issue**: Button handler not wired - tapping doesn't trigger navigation
**Evidence**: `next_incomplete_wiring_test.dart` will fail
**Fix**: Wire button onPressed to call repository and navigate to result

## Flow 2: Dictionary List → Display
```
UI: DictionaryScreen.listView
    ↓
Repository: DictionaryRepository.fetchDictionary()
    ↓
HTTP: GET /api/v1/dictionary
    ↓
Router: dictionary.py::list_terms()
    ↓
DB: Query dictionary_terms table
```

**Status**: 🔴 BROKEN
**Issue**: API returns 500 - missing table or query implementation
**Evidence**: `test_dictionary_list.py` fails with 500
**Fix**: Create dictionary_terms table and implement query logic

## Flow 3: Dictionary Edit → Update
```
UI: DictionaryScreen.editForm.onSubmit
    ↓
Repository: DictionaryRepository.updateEntry()
    ↓
HTTP: PUT /api/v1/dictionary/{id}
    ↓
Router: dictionary.py::update_term()
    ↓
DB: UPDATE dictionary_terms
```

**Status**: 🔴 BROKEN
**Issue**: Router handler missing - returns 500
**Evidence**: `edit_flow_test.dart` will fail
**Fix**: Implement PUT handler in dictionary router

## Flow 4: Workspace Import → Process File
```
UI: WorkspaceScreen.importButton.onPressed
    ↓
Repository: WorkspaceRepository.importFile()
    ↓
HTTP: POST /api/v1/import (multipart)
    ↓
Router: importer.py::import_file()
    ↓
DB: Parse Excel → INSERT nodes
```

**Status**: 🔴 BROKEN
**Issue**: Import succeeds but no data persists to database
**Evidence**: `test_import_excel_persists.py` fails - baseline unchanged
**Fix**: Implement database write logic in import handler

## Flow 5: VM Root Creation → Create Tree
```
UI: TreeCreationWizard.submitButton
    ↓
Repository: TreeRepository.createVmRoot()
    ↓
HTTP: POST /api/v1/tree/roots
    ↓
Router: tree.py::create_vm_root()
    ↓
DB: INSERT root + 5 children
```

**Status**: 🔴 BROKEN
**Issue**: Router handler missing - returns 500
**Evidence**: `test_vm_root_create.py` fails with 500
**Fix**: Implement POST /tree/roots handler

## Flow 6: Tree Stats → Display Metrics
```
UI: DashboardScreen.statsWidget
    ↓
Repository: TreeRepository.getStats()
    ↓
HTTP: GET /api/v1/tree/stats
    ↓
Router: tree.py::get_tree_stats()
    ↓
DB: COUNT nodes, roots, leaves, etc.
```

**Status**: 🔴 BROKEN
**Issue**: Route precedence - /tree/{parent_id} takes precedence
**Evidence**: `test_tree_stats_route.py` fails with 422
**Fix**: Reorder routes or use explicit path matching

## Flow 7: Outcomes LLM Health → Gate Button
```
UI: OutcomesDetailScreen.llmButton visibility
    ↓
Repository: OutcomesRepository.checkLlmHealth()
    ↓
HTTP: GET /api/v1/llm/health
    ↓
Router: llm.py::health_check()
    ↓
Service: Check LLM service availability
```

**Status**: 🔴 BROKEN
**Issue**: Health check result not wired to button visibility
**Evidence**: `validation_and_llm_gating_test.dart` will fail
**Fix**: Use health check result to control button visibility

## Flow 8: Outcomes Client Validation → Reject Invalid
```
UI: OutcomesDetailScreen.form.onSubmit
    ↓
Validation: Client-side 7-word + no dosing check
    ↓
If valid: Repository: OutcomesRepository.updateOutcomes()
    ↓
HTTP: PUT /api/v1/outcomes/{node_id}
```

**Status**: 🔴 BROKEN
**Issue**: No client-side validation implemented
**Evidence**: `validation_and_llm_gating_test.dart` will fail
**Fix**: Add form validation for word count and dosing tokens

## Flow 9: Import Error Handling → Surface Details
```
UI: WorkspaceScreen.importStatusPanel
    ↓
Error Details: Show row, col, expected, received
    ↓
HTTP Response: 422 with validation details
    ↓
Router: importer.py validation errors
```

**Status**: 🔴 BROKEN
**Issue**: 422 details not surfaced in UI error display
**Evidence**: `import_ui_contract_test.dart` will fail
**Fix**: Parse and display validation error details in UI

## Flow 10: Dictionary Edit → No Home Redirect
```
UI: DictionaryScreen.editButton.onPressed
    ↓
Navigation: Should open edit form, not redirect to Home
    ↓
Check: Null args should not trigger Home redirect
```

**Status**: 🔴 BROKEN
**Issue**: Edit flow redirects to Home when args are null
**Evidence**: `edit_flow_test.dart` will fail
**Fix**: Fix navigation logic to handle null args properly

## Working Flows (Reference)

### Health Check
```
UI: AnyScreen.healthIndicator
    ↓
Repository: HealthRepository.checkHealth()
    ↓
HTTP: GET /api/v1/health
    ↓
Router: health.py::health_check()
    ↓
DB: Check connections and return status
```
**Status**: 🟢 WORKING

### Next Incomplete Parent (API Only)
```
Repository: EditTreeRepository.fetchNextIncompleteParent()
    ↓
HTTP: GET /api/v1/tree/next-incomplete-parent
    ↓
Router: tree.py::next_incomplete_parent()
    ↓
DB: Query for incomplete parents
```
**Status**: 🟢 WORKING (API), 🔴 BROKEN (UI wiring)

## Summary of Broken Links

| Flow | Component | Issue | Test File |
|------|-----------|-------|-----------|
| 1 | Edit Tree Button | Handler not wired | next_incomplete_wiring_test.dart |
| 2 | Dictionary API | Missing table/query | test_dictionary_list.py |
| 3 | Dictionary Update | Missing PUT handler | edit_flow_test.dart |
| 4 | Import Persistence | No DB writes | test_import_excel_persists.py |
| 5 | VM Root Creation | Missing POST handler | test_vm_root_create.py |
| 6 | Tree Stats Route | Precedence conflict | test_tree_stats_route.py |
| 7 | LLM Gating | Not wired to UI | validation_and_llm_gating_test.dart |
| 8 | Client Validation | Not implemented | validation_and_llm_gating_test.dart |
| 9 | Error Details | Not surfaced | import_ui_contract_test.dart |
| 10 | Edit Navigation | Redirects to Home | edit_flow_test.dart |

## Fix Priority Order

1. **High Priority** (Blockers):
   - Flow 6: Tree stats route precedence
   - Flow 2: Dictionary table/query
   - Flow 5: VM root creation handler

2. **Medium Priority** (UX Issues):
   - Flow 1: Next incomplete wiring
   - Flow 10: Dictionary navigation
   - Flow 7: LLM gating

3. **Low Priority** (Enhancements):
   - Flow 3: Dictionary update handler
   - Flow 4: Import persistence
   - Flow 8: Client validation
   - Flow 9: Error details

*Note: All broken flows have corresponding test files that will fail until fixes are implemented.*
