# Design Decisions - Phase 6

## CSV Header Contract Freeze
- **Decision**: CSV export headers are frozen at exactly 8 columns
- **Rationale**: Prevents schema drift and ensures consistent data exchange
- **Impact**: Any header change requires version bump and comprehensive test updates
- **Enforcement**: Tests compare against fixture exactly; UI shows header preview

## Outcomes Edit = Leaf-Only
- **Decision**: Triage editing restricted to leaf nodes only
- **Rationale**: Maintains data integrity; non-leaves represent decision points, not outcomes
- **Implementation**: UI disables controls for non-leaves; API validates and returns clear errors
- **User Experience**: Clear feedback when attempting to edit non-leaf nodes

## LLM OFF by Default
- **Decision**: Large Language Model integration disabled by default
- **Rationale**: Safety and medical decision-support compliance
- **UI Behavior**: No dosing/diagnosis suggestions shown; clear indication when LLM unavailable
- **Feature Flag**: Controlled via `/llm/health` endpoint and settings

## Streamlit API-Only Architecture
- **Decision**: Streamlit adapter communicates exclusively through API
- **Rationale**: Maintains separation of concerns; prevents direct database access
- **Enforcement**: Forbidden imports test; all data operations via HTTP requests
- **Benefits**: Consistent data validation, audit trail, multi-client support

## Dual Mount Strategy
- **Decision**: All endpoints available at both `/` and `/api/v1` prefixes
- **Rationale**: Backward compatibility and versioning flexibility
- **Implementation**: Router mounting in FastAPI app
- **Testing**: Both paths tested for consistency

## Missing Slots Detection
- **Decision**: Real-time detection of parents with incomplete child slots
- **Rationale**: Enforces the "exactly 5 children" invariant
- **Implementation**: SQL query with GROUP_CONCAT and HAVING clause
- **User Experience**: Clear visibility into data integrity issues

## Triage Search and Filter
- **Decision**: Flexible search across triage records with leaf-only filtering
- **Rationale**: Efficient navigation of large triage datasets
- **Implementation**: Parameterized SQL with optional text search
- **Performance**: Indexed queries for fast response times

## Inline Editing with Validation
- **Decision**: Inline editing in triage grid with immediate validation
- **Rationale**: Improves user experience and data quality
- **Implementation**: Client-side validation + server-side enforcement
- **Error Handling**: Clear feedback for validation failures
