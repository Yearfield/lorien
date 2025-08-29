import 'package:shared_preferences/shared_preferences.dart';

/// Returns normalized API base URL that always ends with `/api/v1/` (trailing slash).
/// Examples:
///  - in: http://127.0.0.1:8000           -> http://127.0.0.1:8000/api/v1/
///  - in: http://localhost:8000/api/v1     -> http://localhost:8000/api/v1/
///  - in: http://localhost:8000/api/v1/    -> http://localhost:8000/api/v1/
///  - in: (missing/empty)                  -> http://127.0.0.1:8000/api/v1/
String resolveApiBaseUrl() {
  final defined = const String.fromEnvironment('API_BASE_URL', defaultValue: '');
  var base = defined.trim().isEmpty ? 'http://127.0.0.1:8000' : defined.trim();
  // Strip any existing /api/v1[/] and re-append exactly once with trailing slash.
  base = base.replaceFirst(RegExp(r'/api/v1/?$'), '');
  base = '${base.replaceAll(RegExp(r'/+$'), '')}/api/v1/';
  return base;
}

class Env {
  static const String _baseUrlKey = 'api_base_url';
  static const String _themeModeKey = 'theme_mode';
  
  static const String defaultBaseUrl = 'http://localhost:8000/api/v1';
  
  static Future<String> getApiBaseUrl() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_baseUrlKey) ?? defaultBaseUrl;
  }
  
  static Future<void> setApiBaseUrl(String baseUrl) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_baseUrlKey, baseUrl);
  }
  
  static Future<String> getThemeMode() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_themeModeKey) ?? 'system';
  }
  
  static Future<void> setThemeMode(String themeMode) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_themeModeKey, themeMode);
  }
  
  static Future<void> clearAll() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }
}
