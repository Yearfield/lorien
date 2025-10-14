# Dictionary Search Error Fix

## Issue

The Dictionary search was showing a null safety error: "type 'Null' is not a subtype of type 'String' in type cast" when searching for terms like "hyper".

## Root Cause

The JSON parsing code in the generated Flutter DTOs was using camelCase field names (`isRedFlag`, `avgChildrenCount`, etc.) instead of the snake_case field names that the API actually returns (`is_red_flag`, `avg_children_count`, etc.).

## Fix Applied

Updated the generated JSON parsing code in `/home/jharm/Lorien/ui_flutter/lib/features/dictionary/data/dictionary_dto.g.dart`:

### Before (Incorrect)

```dart
isRedFlag: json['isRedFlag'] as bool? ?? false,
avgChildrenCount: (json['avgChildrenCount'] as num?)?.toInt() ?? 0,
conflictsCount: (json['conflictsCount'] as num?)?.toInt() ?? 0,
createdAt: json['createdAt'] as String,
updatedAt: json['updatedAt'] as String,
```

### After (Fixed)

```dart
isRedFlag: json['is_red_flag'] as bool? ?? false,
avgChildrenCount: (json['avg_children_count'] as num?)?.toInt() ?? 0,
conflictsCount: (json['conflicts_count'] as num?)?.toInt() ?? 0,
createdAt: json['created_at'] as String,
updatedAt: json['updated_at'] as String,
```

## Verification

- ✅ API endpoints working correctly
- ✅ Search returns proper results (e.g., "hyper" finds "Hypertension")
- ✅ Term details API working
- ✅ Tree relationships API working
- ✅ Flutter app compiles successfully
- ✅ JSON parsing code updated correctly

## Next Steps

To apply the fix, you need to **restart the Flutter app**:

1. **Stop the current Flutter app** (if running)
2. **Restart Flutter**:

   ```bash
   cd /home/jharm/Lorien/ui_flutter
   flutter run -d linux --dart-define=API_BASE_URL=http://127.0.0.1:8000
   ```

The search functionality should now work correctly without null safety errors.
