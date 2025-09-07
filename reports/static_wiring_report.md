# Lorien Static Wiring Report

## Overview
This report documents the wiring between UI components, repositories, and API endpoints in the Lorien application. It identifies the current state of implementation and gaps that need to be addressed.

## UI → Repository → HTTP Flow Analysis

### 1. Edit Tree Screen
**Component**: `EditTreeScreen`
**Repository**: `EditTreeRepository`
**Endpoints**:
- `GET /api/v1/tree/parents/incomplete` - List incomplete parents
- `GET /api/v1/tree/next-incomplete-parent` - Get next incomplete parent

**Current Status**: PARTIAL
**Issues**:
- List loading works
- Next incomplete parent button exists but handler may not be wired
- Navigation to specific parent may not be implemented

**Test Coverage**: `next_incomplete_wiring_test.dart`
**Expected Test Result**: FAIL (handler not wired)

### 2. Dictionary Screen
**Component**: `DictionaryScreen`
**Repository**: `DictionaryRepository`
**Endpoints**:
- `GET /api/v1/dictionary` - List dictionary entries
- `POST /api/v1/dictionary` - Create new entry
- `PUT /api/v1/dictionary/{id}` - Update entry
- `DELETE /api/v1/dictionary/{id}` - Delete entry

**Current Status**: PARTIAL
**Issues**:
- List display works
- Edit flow may redirect to Home instead of opening edit form
- Form validation may not be properly wired

**Test Coverage**: `edit_flow_test.dart`
**Expected Test Result**: FAIL (null args redirect to Home)

### 3. Workspace Screen
**Component**: `WorkspaceScreen`
**Repository**: `WorkspaceRepository`
**Endpoints**:
- `POST /api/v1/import` - Import Excel/CSV files
- `GET /api/v1/tree/stats` - Get tree statistics

**Current Status**: PARTIAL
**Issues**:
- UI components exist
- File picker may be implemented
- Import status feedback may not be wired
- Error handling for 422 validation may not surface details properly

**Test Coverage**: `import_ui_contract_test.dart`
**Expected Test Result**: MIXED (UI exists, wiring partial)

### 4. Outcomes Detail Screen
**Component**: `OutcomesDetailScreen`
**Repository**: `OutcomesRepository`
**Endpoints**:
- `GET /api/v1/llm/health` - Check LLM availability
- `PUT /api/v1/outcomes/{node_id}` - Update outcomes
- `POST /api/v1/llm/fill` - LLM-assisted content generation

**Current Status**: PARTIAL
**Issues**:
- LLM health check may not be wired to button visibility
- Client-side validation (7 words, no dosing) may not be implemented
- LLM button gating may not work

**Test Coverage**: `validation_and_llm_gating_test.dart`
**Expected Test Result**: FAIL (LLM gating not implemented)

## Repository Implementation Status

### EditTreeRepository
**Methods**:
- `fetchIncompleteParents()` - ✅ Implemented
- `fetchNextIncompleteParent()` - ❓ Unknown
- `navigateToParent()` - ❓ Unknown

### DictionaryRepository
**Methods**:
- `fetchDictionary()` - ✅ Implemented
- `createEntry()` - ❓ Unknown
- `updateEntry()` - ❓ Unknown
- `deleteEntry()` - ❓ Unknown

### WorkspaceRepository
**Methods**:
- `importFile()` - ❓ Unknown
- `getStats()` - ❓ Unknown

### OutcomesRepository
**Methods**:
- `checkLlmHealth()` - ❓ Unknown
- `updateOutcomes()` - ❓ Unknown
- `generateWithLlm()` - ❓ Unknown

## API Endpoint Status

### Working Endpoints
- `GET /api/v1/tree/parents/incomplete` ✅
- `GET /api/v1/dictionary` ✅
- `GET /api/v1/tree/stats` ❓ (route precedence issue)
- `GET /api/v1/health` ✅
- `GET /api/v1/llm/health` ✅

### Broken/Missing Endpoints
- `GET /api/v1/tree/stats` ❌ (422 due to route precedence)
- `POST /api/v1/tree/roots` ❌ (500 - missing handler)
- `POST /api/v1/import` ❌ (no-op/placeholder)
- `PUT /api/v1/dictionary/{id}` ❌ (500 - missing handler)

## Wiring Gaps Summary

1. **Route Precedence**: `/tree/stats` returns 422 instead of stats
2. **Missing Handlers**: VM root creation, dictionary CRUD operations
3. **Import Placeholder**: Excel import doesn't persist data
4. **UI Wiring**: Next incomplete navigation, LLM gating, validation
5. **Error Handling**: 422 details not surfaced in UI

## Recommended Fix Order

1. Fix route precedence for `/tree/stats`
2. Implement VM root creation handler
3. Add dictionary CRUD handlers
4. Wire import persistence
5. Fix UI wiring issues
6. Improve error handling

## Test Status

| Component | Test File | Expected Result | Current Status |
|-----------|-----------|-----------------|----------------|
| Edit Tree | `next_incomplete_wiring_test.dart` | FAIL | Created |
| Dictionary | `edit_flow_test.dart` | FAIL | Created |
| Workspace | `import_ui_contract_test.dart` | MIXED | Created |
| Outcomes | `validation_and_llm_gating_test.dart` | FAIL | Created |

*Note: All tests are designed to FAIL where functionality is missing, ensuring they turn green when implementations are added.*
