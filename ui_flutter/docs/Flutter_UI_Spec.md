# Flutter UI Spec

## 1. Overview

**Goal**: Cross-platform Flutter application for decision tree management with offline-first storage and real-time API integration.

**Platforms**: Desktop (Windows, macOS, Linux) + Mobile (Android, iOS)

**API Base URL**: Configurable at runtime, default `http://localhost:8000`, persisted using SharedPreferences

**Version**: 1.0.0 (shown in About section)

## 2. Screens

### Splash Screen
- **Purpose**: Health check → route to appropriate screen
- **Features**: 
  - App logo and title display
  - Connection status check
  - Automatic routing to Home (if connected) or Settings (if disconnected)
  - Loading indicator with status text

### Home Screen
- **Purpose**: Status + shortcuts to main features
- **Features**:
  - Connection status indicator (green/amber/red)
  - Quick action cards for Editor, Red Flags, Calculator, Settings
  - Real-time connection status updates
  - Navigation to Settings if connection issues

### Editor Screen
- **Purpose**: Parent list, search, "Skip to next incomplete parent"
- **Features**:
  - Search parents by text (top bar)
  - "Skip to next incomplete parent" button (prominent)
  - Parent list with infinite/lazy loading
  - Navigation to parent detail screens
  - Empty state with helpful messaging

### Parent Detail Screen
- **Purpose**: Five slots UI, triage/actions panel
- **Features**:
  - Five slot cards (1-5) in grid layout
  - Each slot shows label or "Empty" state
  - Tap to add/replace via search dialog
  - Save/Apply functionality with optimistic updates
  - Reorder within 1-5 slots (simple swap UI)
  - Secondary panel for Diagnostic Triage & Actions
  - Inline edit & save for triage data

### Flags Screen
- **Purpose**: Search + assign/unassign red flags
- **Features**:
  - Search red flags with debounced input
  - Real-time search results
  - Assign/unassign to current node
  - Live reflect assignment status
  - Empty state for no results

### Calculator Screen
- **Purpose**: Selection → Export CSV
- **Features**:
  - Multi-select of leaf nodes or parent paths
  - Export button triggers GET /calc/export
  - Save file locally with platform-specific paths
  - Success toast with file path
  - "Share" action on mobile platforms

### Settings Screen
- **Purpose**: Base URL, test connection, theme, About
- **Features**:
  - API base URL text field with validation
  - "Test Connection" button with real-time feedback
  - Theme selection (System/Light/Dark)
  - About section with app version
  - Connection status indicator
  - Save settings with persistence

## 3. API Usage

### Health Check
```
GET /health
Response: { "status": "healthy", "version": "1.0.0", "timestamp": "..." }
```

### Tree Management
```
GET /tree/next-incomplete-parent
Response: { "parent_id": 123, "missing_slots": [2, 4] }

GET /tree/{parent_id}/children
Response: [{ "slot": 1, "label": "Mild" }, ...]

POST /tree/{parent_id}/children
Body: { "children": [{ "slot": 1, "label": "Mild" }, ...] }
```

### Triage Management
```
GET /triage/{node_id}
Response: { "diagnostic_triage": "...", "actions": "..." }

PUT /triage/{node_id}
Body: { "diagnostic_triage": "...", "actions": "..." }
```

### Red Flags
```
GET /flags/search?q=term
Response: [{ "id": 1, "name": "High Risk" }, ...]

POST /flags/assign
Body: { "node_id": 123, "red_flag_name": "High Risk" }
```

### Export
```
GET /calc/export
Response: CSV stream with content-disposition header
```

## 4. State Management (Riverpod)

### App Settings Provider
- **Responsibilities**: API base URL, theme mode, connection status
- **Persistence**: SharedPreferences for settings
- **Real-time**: Connection status updates

### Tree Providers
- **Parents Provider**: List of parent nodes with caching
- **Parent Detail Provider**: Children slots for specific parent
- **Next Incomplete Provider**: Current incomplete parent state

### Triage Providers
- **Triage Provider**: Diagnostic triage and actions for nodes
- **Validation**: Real-time validation before API calls

### Flags Providers
- **Search Provider**: Red flag search results with debouncing
- **Assignment Provider**: Current flag assignments per node

### Calculator Providers
- **Selection Provider**: Selected paths/nodes for export
- **Export Provider**: CSV export state and progress

## 5. Error Handling

### Network Errors
- Connection timeout → "Connection timeout. Please check your network."
- Connection error → "Unable to connect to server. Please check the API URL."
- Graceful degradation with offline indicators

### API Errors
- 422 Validation Error → "Validation error: [detail message]"
- 409 Conflict → "Conflict: [detail message]"
- User-friendly error messages with actionable guidance

### UI Error States
- Empty states with helpful messaging
- Loading states with progress indicators
- Error states with retry options
- Busy overlay during long operations

## 6. File Export

### CSV Export
- **Desktop**: Save to Downloads folder
- **Mobile**: Save to Documents folder
- **Platform Integration**: Use path_provider + share_plus
- **File Naming**: `decision_tree_export_YYYYMMDD_HHMMSS.csv`
- **Success Feedback**: Toast with file path and "Open/Share" button

### Share Integration
- **Mobile**: Native share sheet
- **Desktop**: File explorer open
- **Cross-platform**: Consistent user experience

## 7. Theming & Accessibility

### Theme Support
- **Light Theme**: Clean, modern Material Design 3
- **Dark Theme**: Dark surfaces with proper contrast
- **System Theme**: Follows OS preference
- **Custom Colors**: Primary blue, secondary teal, error red

### Accessibility
- **Text Scaling**: Supports system text size
- **Screen Readers**: Proper semantic labels
- **Keyboard Navigation**: Full keyboard support on desktop
- **Color Contrast**: WCAG AA compliant

### Desktop Features
- **Keyboard Shortcuts**:
  - Ctrl/Cmd+F: Search
  - Ctrl/Cmd+S: Save
  - Alt+N: Next incomplete parent
- **Window Management**: Minimum size constraints
- **Native Integration**: Platform-specific behaviors

## 8. Build & Run

### Development Commands
```bash
# Desktop
flutter run -d windows|macos|linux

# Mobile
flutter run -d android|ios

# Code Generation
flutter packages pub run build_runner build
```

### Production Builds
```bash
# Desktop
flutter build windows|macos|linux

# Mobile
flutter build apk|appbundle|ios
```

### Environment Notes
- **Mobile Development**: Use LAN IP (e.g., 192.168.0.10:8000) instead of localhost
- **Desktop Development**: localhost:8000 works fine
- **Cross-platform Testing**: Test on multiple platforms before release

## 9. Limitations & Roadmap

### Current Limitations
- **Offline Queue**: No offline operation queue yet
- **Data Caching**: Limited in-memory caching
- **Real-time Sync**: No WebSocket integration
- **Advanced Search**: Basic text search only

### Future Enhancements
- **Offline Support**: Isar/Hive local database
- **Real-time Updates**: WebSocket integration
- **Advanced Search**: Full-text search with filters
- **Data Import**: Excel/CSV import functionality
- **User Management**: Multi-user support
- **App Store**: Package for distribution

### Performance Considerations
- **Lazy Loading**: Implement for large datasets
- **Image Optimization**: Optimize assets for mobile
- **Memory Management**: Proper disposal of resources
- **Network Optimization**: Request caching and batching

### Security Considerations
- **API Security**: HTTPS enforcement
- **Data Validation**: Client-side validation
- **Error Handling**: No sensitive data in error messages
- **Platform Security**: Follow platform security guidelines
