# Decision Tree Manager - Flutter UI

Cross-platform Flutter application for managing decision tree structures with offline-first storage.

## Features

- **Cross-platform**: Desktop (Windows, macOS, Linux) and Mobile (Android, iOS)
- **API Integration**: Connects to FastAPI backend for data management
- **Offline-first**: Local storage with sync capabilities
- **Real-time Updates**: Live connection status and data synchronization
- **Modern UI**: Material Design 3 with light/dark theme support

## Prerequisites

- Flutter SDK 3.10.0 or higher
- Dart SDK 3.0.0 or higher
- Android Studio / VS Code with Flutter extensions
- For desktop: Platform-specific development tools

## Setup

1. **Install Dependencies**
   ```bash
   flutter pub get
   ```

2. **Generate Code** (if using freezed/json_serializable)
   ```bash
   flutter packages pub run build_runner build
   ```

3. **Configure API Base URL**
   - Launch the app
   - Go to Settings
   - Enter your API base URL (default: http://localhost:8000)
   - Test connection

## Development Commands

### Desktop Development
```bash
# Windows
flutter run -d windows

# macOS
flutter run -d macos

# Linux
flutter run -d linux
```

### Mobile Development
```bash
# Android
flutter run -d android

# iOS (macOS only)
flutter run -d ios
```

### Building for Production

#### Desktop
```bash
# Windows
flutter build windows

# macOS
flutter build macos

# Linux
flutter build linux
```

#### Mobile
```bash
# Android APK
flutter build apk

# Android App Bundle
flutter build appbundle

# iOS (macOS only)
flutter build ios
```

## Project Structure

```
lib/
├── main.dart                 # App entry point
├── app.dart                  # Main app widget
├── routing/
│   └── app_router.dart       # Navigation configuration
├── theme/
│   └── app_theme.dart        # Theme configuration
├── data/
│   ├── api_client.dart       # HTTP client with Dio
│   ├── dto/                  # Data transfer objects
│   └── repos/                # Repository layer
├── state/                    # Riverpod state management
├── screens/                  # UI screens
│   ├── editor/              # Tree editing screens
│   ├── flags/               # Red flags management
│   ├── calc/                # Calculator/export
│   └── settings/            # App configuration
├── widgets/                  # Reusable UI components
└── utils/                    # Utility functions
```

## API Integration

The app connects to the FastAPI backend using the following endpoints:

- `GET /api/v1/health` - Health check
- `GET /tree/next-incomplete-parent` - Get next incomplete parent
- `GET /tree/{parent_id}/children` - Get children for a parent
- `POST /tree/{parent_id}/children` - Upsert children
- `GET /triage/{node_id}` - Get triage data
- `PUT /triage/{node_id}` - Update triage data
- `GET /flags/search?q=term` - Search red flags
- `POST /flags/assign` - Assign red flag
- `GET /calc/export` - Export CSV

## Configuration

### API Base URL
- Default: `http://localhost:8000/api/v1`
- Configurable in Settings screen
- Persisted using SharedPreferences
- Supports LAN IP for mobile development (e.g., `http://192.168.0.10:8000`)

### Theme
- System (follows OS theme)
- Light theme
- Dark theme
- Persisted across app restarts

## Development Notes

### State Management
- Uses Riverpod for state management
- Providers for API client, settings, and data
- Automatic state persistence

### Error Handling
- Network error handling with user-friendly messages
- Validation error mapping (422, 409)
- Graceful degradation for offline scenarios

### File Operations
- CSV export using path_provider and share_plus
- Platform-specific file saving
- Share functionality on mobile

## Troubleshooting

### Connection Issues
1. Verify API server is running
2. Check API base URL in Settings
3. Ensure firewall allows connections
4. For mobile: Use LAN IP instead of localhost

### Build Issues
1. Run `flutter clean`
2. Run `flutter pub get`
3. Regenerate code: `flutter packages pub run build_runner build`

### Platform-Specific Issues
- **Windows**: Ensure Visual Studio Build Tools installed
- **macOS**: Xcode command line tools required
- **Linux**: Install required dependencies for your distribution
- **Android**: Android SDK and emulator/device setup
- **iOS**: Xcode and iOS Simulator (macOS only)

## Contributing

1. Follow Flutter coding standards
2. Use meaningful commit messages
3. Test on multiple platforms
4. Update documentation as needed

## License

This project is part of the Decision Tree Manager application.
