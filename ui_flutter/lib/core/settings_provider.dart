import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:file_picker/file_picker.dart';
import 'package:open_filex/open_filex.dart';
import 'dart:convert';
import 'dart:io';

// Export format options
enum CsvEncoding {
  utf8,
  utf8Bom,
  latin1,
}

enum CsvDelimiter {
  comma,
  semicolon,
  tab,
}

class ExportSettings {
  final CsvEncoding encoding;
  final CsvDelimiter delimiter;
  final bool includeHeaders;
  final bool includeTimestamps;

  const ExportSettings({
    this.encoding = CsvEncoding.utf8,
    this.delimiter = CsvDelimiter.comma,
    this.includeHeaders = true,
    this.includeTimestamps = true,
  });

  ExportSettings copyWith({
    CsvEncoding? encoding,
    CsvDelimiter? delimiter,
    bool? includeHeaders,
    bool? includeTimestamps,
  }) {
    return ExportSettings(
      encoding: encoding ?? this.encoding,
      delimiter: delimiter ?? this.delimiter,
      includeHeaders: includeHeaders ?? this.includeHeaders,
      includeTimestamps: includeTimestamps ?? this.includeTimestamps,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'encoding': encoding.name,
      'delimiter': delimiter.name,
      'includeHeaders': includeHeaders,
      'includeTimestamps': includeTimestamps,
    };
  }

  factory ExportSettings.fromJson(Map<String, dynamic> json) {
    return ExportSettings(
      encoding: CsvEncoding.values.firstWhere(
        (e) => e.name == json['encoding'],
        orElse: () => CsvEncoding.utf8,
      ),
      delimiter: CsvDelimiter.values.firstWhere(
        (e) => e.name == json['delimiter'],
        orElse: () => CsvDelimiter.comma,
      ),
      includeHeaders: json['includeHeaders'] ?? true,
      includeTimestamps: json['includeTimestamps'] ?? true,
    );
  }
}

// Debug settings model
class DebugSettings {
  final bool debugMode;
  final bool apiLogging;
  final bool mockData;
  final bool verboseLogging;
  final bool showPerformanceMetrics;

  const DebugSettings({
    this.debugMode = false,
    this.apiLogging = false,
    this.mockData = false,
    this.verboseLogging = false,
    this.showPerformanceMetrics = false,
  });

  DebugSettings copyWith({
    bool? debugMode,
    bool? apiLogging,
    bool? mockData,
    bool? verboseLogging,
    bool? showPerformanceMetrics,
  }) {
    return DebugSettings(
      debugMode: debugMode ?? this.debugMode,
      apiLogging: apiLogging ?? this.apiLogging,
      mockData: mockData ?? this.mockData,
      verboseLogging: verboseLogging ?? this.verboseLogging,
      showPerformanceMetrics: showPerformanceMetrics ?? this.showPerformanceMetrics,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'debugMode': debugMode,
      'apiLogging': apiLogging,
      'mockData': mockData,
      'verboseLogging': verboseLogging,
      'showPerformanceMetrics': showPerformanceMetrics,
    };
  }

  factory DebugSettings.fromJson(Map<String, dynamic> json) {
    return DebugSettings(
      debugMode: json['debugMode'] ?? false,
      apiLogging: json['apiLogging'] ?? false,
      mockData: json['mockData'] ?? false,
      verboseLogging: json['verboseLogging'] ?? false,
      showPerformanceMetrics: json['showPerformanceMetrics'] ?? false,
    );
  }
}

// Settings model
class AppSettings {
  final String apiBaseUrl;
  final ThemeMode themeMode;
  final bool autoSave;
  final bool showConfirmations;
  final ExportSettings exportSettings;
  final int autoSaveDelayMs;
  final DebugSettings debugSettings;

  const AppSettings({
    this.apiBaseUrl = 'http://127.0.0.1:8000/api/v1',
    this.themeMode = ThemeMode.system,
    this.autoSave = true,
    this.showConfirmations = true,
    this.exportSettings = const ExportSettings(),
    this.autoSaveDelayMs = 1000, // 1 second debounce
    this.debugSettings = const DebugSettings(),
  });

  AppSettings copyWith({
    String? apiBaseUrl,
    ThemeMode? themeMode,
    bool? autoSave,
    bool? showConfirmations,
    ExportSettings? exportSettings,
    int? autoSaveDelayMs,
    DebugSettings? debugSettings,
  }) {
    return AppSettings(
      apiBaseUrl: apiBaseUrl ?? this.apiBaseUrl,
      themeMode: themeMode ?? this.themeMode,
      autoSave: autoSave ?? this.autoSave,
      showConfirmations: showConfirmations ?? this.showConfirmations,
      exportSettings: exportSettings ?? this.exportSettings,
      autoSaveDelayMs: autoSaveDelayMs ?? this.autoSaveDelayMs,
      debugSettings: debugSettings ?? this.debugSettings,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'apiBaseUrl': apiBaseUrl,
      'themeMode': themeMode.name,
      'autoSave': autoSave,
      'showConfirmations': showConfirmations,
      'exportSettings': exportSettings.toJson(),
      'autoSaveDelayMs': autoSaveDelayMs,
      'debugSettings': debugSettings.toJson(),
    };
  }

  factory AppSettings.fromJson(Map<String, dynamic> json) {
    return AppSettings(
      apiBaseUrl: json['apiBaseUrl'] ?? 'http://127.0.0.1:8000/api/v1',
      themeMode: ThemeMode.values.firstWhere(
        (e) => e.name == json['themeMode'],
        orElse: () => ThemeMode.system,
      ),
      autoSave: json['autoSave'] ?? true,
      showConfirmations: json['showConfirmations'] ?? true,
      exportSettings: json['exportSettings'] != null
        ? ExportSettings.fromJson(json['exportSettings'] as Map<String, dynamic>)
        : const ExportSettings(),
      autoSaveDelayMs: json['autoSaveDelayMs'] ?? 1000,
      debugSettings: json['debugSettings'] != null
        ? DebugSettings.fromJson(json['debugSettings'] as Map<String, dynamic>)
        : const DebugSettings(),
    );
  }
}

// Database status model
class DatabaseStatus {
  final String? path;
  final String? journalMode;
  final int? tableCount;
  final int? nodeCount;
  final String? integrity;
  final int? objectCount;
  final bool? foreignKeys;
  final int? pageSize;
  final String? version;

  const DatabaseStatus({
    this.path,
    this.journalMode,
    this.tableCount,
    this.nodeCount,
    this.integrity,
    this.objectCount,
    this.foreignKeys,
    this.pageSize,
    this.version,
  });

  factory DatabaseStatus.fromHealthData(Map<String, dynamic> healthData) {
    final dbData = healthData['db'] as Map<String, dynamic>?;
    return DatabaseStatus(
      path: dbData?['path'],
      journalMode: dbData?['journal_mode'],
      tableCount: dbData?['tables'],
      nodeCount: dbData?['nodes'],
      integrity: dbData?['integrity'],
      objectCount: dbData?['objects'],
      foreignKeys: dbData?['foreign_keys'],
      pageSize: dbData?['page_size'],
      version: dbData?['version'],
    );
  }

  bool get isHealthy => integrity?.toLowerCase() == 'ok';
  String get statusText => isHealthy ? 'Healthy' : 'Issues detected';
}

// Connection status model
class ConnectionStatus {
  final bool isConnected;
  final String? error;
  final DateTime? lastChecked;
  final Map<String, dynamic>? healthData;
  final DatabaseStatus? databaseStatus;
  final String? apiVersion;
  final Map<String, bool>? features;

  const ConnectionStatus({
    this.isConnected = false,
    this.error,
    this.lastChecked,
    this.healthData,
    this.databaseStatus,
    this.apiVersion,
    this.features,
  });

  ConnectionStatus copyWith({
    bool? isConnected,
    String? error,
    DateTime? lastChecked,
    Map<String, dynamic>? healthData,
    DatabaseStatus? databaseStatus,
    String? apiVersion,
    Map<String, bool>? features,
  }) {
    return ConnectionStatus(
      isConnected: isConnected ?? this.isConnected,
      error: error,
      lastChecked: lastChecked ?? this.lastChecked,
      healthData: healthData ?? this.healthData,
      databaseStatus: databaseStatus ?? this.databaseStatus,
      apiVersion: apiVersion ?? this.apiVersion,
      features: features ?? this.features,
    );
  }
}

// Settings provider
class SettingsNotifier extends StateNotifier<AppSettings> {
  SettingsNotifier() : super(const AppSettings()) {
    _loadSettings();
  }

  static const String _settingsKey = 'app_settings';

  Future<void> _loadSettings() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final settingsJson = prefs.getString(_settingsKey);
      if (settingsJson != null) {
        final settingsMap = json.decode(settingsJson) as Map<String, dynamic>;
        state = AppSettings.fromJson(settingsMap);
      }
    } catch (e) {
      // If loading fails, use default settings
      state = const AppSettings();
    }
  }

  Future<void> _saveSettings() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_settingsKey, json.encode(state.toJson()));
    } catch (e) {
      // Handle save error silently for now
    }
  }

  Future<void> updateApiBaseUrl(String url) async {
    // Basic URL validation
    if (url.isEmpty) return;

    // Ensure URL ends with /api/v1 if not already
    String normalizedUrl = url.trim();
    if (!normalizedUrl.endsWith('/api/v1')) {
      normalizedUrl = normalizedUrl.replaceAll(RegExp(r'/+$'), '');
      normalizedUrl = '$normalizedUrl/api/v1';
    }

    state = state.copyWith(apiBaseUrl: normalizedUrl);
    await _saveSettings();
  }

  Future<void> updateThemeMode(ThemeMode themeMode) async {
    state = state.copyWith(themeMode: themeMode);
    await _saveSettings();
  }

  Future<void> updateAutoSave(bool autoSave) async {
    state = state.copyWith(autoSave: autoSave);
    await _saveSettings();
  }

  Future<void> updateShowConfirmations(bool showConfirmations) async {
    state = state.copyWith(showConfirmations: showConfirmations);
    await _saveSettings();
  }

  Future<void> updateExportSettings(ExportSettings exportSettings) async {
    state = state.copyWith(exportSettings: exportSettings);
    await _saveSettings();
  }

  Future<void> updateAutoSaveDelay(int delayMs) async {
    state = state.copyWith(autoSaveDelayMs: delayMs);
    await _saveSettings();
  }

  Future<void> updateDebugSettings(DebugSettings debugSettings) async {
    state = state.copyWith(debugSettings: debugSettings);
    await _saveSettings();
  }

  Future<void> resetToDefaults() async {
    state = const AppSettings();
    await _saveSettings();
  }

  Future<void> clearAllData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.clear();
      state = const AppSettings();
    } catch (e) {
      // Handle error silently for now
    }
  }

  Future<String?> createBackup() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final settingsJson = json.encode(state.toJson());
      final timestamp = DateTime.now().toIso8601String().replaceAll(':', '-');
      final filename = 'lorien_settings_backup_$timestamp.json';

      final directory = await getApplicationDocumentsDirectory();
      final file = File('${directory.path}/$filename');
      await file.writeAsString(settingsJson);

      return file.path;
    } catch (e) {
      return null;
    }
  }

  Future<bool> restoreFromBackup(String filePath) async {
    try {
      final file = File(filePath);
      if (!await file.exists()) return false;

      final content = await file.readAsString();
      final settingsMap = json.decode(content) as Map<String, dynamic>;
      final restoredSettings = AppSettings.fromJson(settingsMap);

      state = restoredSettings;
      await _saveSettings();
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<String?> exportSettings() async {
    try {
      final settingsJson = json.encode(state.toJson());
      final timestamp = DateTime.now().toIso8601String().replaceAll(':', '-');
      final filename = 'lorien_settings_export_$timestamp.json';

      final directory = await getApplicationDocumentsDirectory();
      final file = File('${directory.path}/$filename');
      await file.writeAsString(settingsJson);

      return file.path;
    } catch (e) {
      return null;
    }
  }
}

// Connection status provider
class ConnectionStatusNotifier extends StateNotifier<ConnectionStatus> {
  ConnectionStatusNotifier(this._settingsNotifier) : super(const ConnectionStatus());

  final SettingsNotifier _settingsNotifier;
  final Dio _dio = Dio(BaseOptions(
    connectTimeout: const Duration(seconds: 5),
    receiveTimeout: const Duration(seconds: 5),
  ));

  Future<void> testConnection() async {
    final apiBaseUrl = _settingsNotifier.state.apiBaseUrl;

    try {
      state = state.copyWith(
        isConnected: false,
        error: null,
        lastChecked: DateTime.now(),
      );

      final response = await _dio.get('$apiBaseUrl/health');

      if (response.statusCode == 200) {
        final healthData = response.data as Map<String, dynamic>;
        final databaseStatus = DatabaseStatus.fromHealthData(healthData);
        state = state.copyWith(
          isConnected: true,
          healthData: healthData,
          databaseStatus: databaseStatus,
          apiVersion: healthData['version'],
          features: Map<String, bool>.from(healthData['features'] ?? {}),
          lastChecked: DateTime.now(),
        );
      } else {
        state = state.copyWith(
          isConnected: false,
          error: 'HTTP ${response.statusCode}',
          lastChecked: DateTime.now(),
        );
      }
    } catch (e) {
      String errorMessage = 'Connection failed';
      if (e is DioException) {
        switch (e.type) {
          case DioExceptionType.connectionTimeout:
            errorMessage = 'Connection timeout';
            break;
          case DioExceptionType.receiveTimeout:
            errorMessage = 'Receive timeout';
            break;
          case DioExceptionType.connectionError:
            errorMessage = 'Connection error - check URL and network';
            break;
          case DioExceptionType.badResponse:
            errorMessage = 'Bad response from server';
            break;
          default:
            errorMessage = 'Network error: ${e.message}';
        }
      }

      state = state.copyWith(
        isConnected: false,
        error: errorMessage,
        lastChecked: DateTime.now(),
      );
    }
  }
}

// Providers
final settingsProvider = StateNotifierProvider<SettingsNotifier, AppSettings>((ref) {
  return SettingsNotifier();
});

final connectionStatusProvider = StateNotifierProvider<ConnectionStatusNotifier, ConnectionStatus>((ref) {
  final settingsNotifier = ref.watch(settingsProvider.notifier);
  return ConnectionStatusNotifier(settingsNotifier);
});

// Using Flutter's built-in ThemeMode enum
